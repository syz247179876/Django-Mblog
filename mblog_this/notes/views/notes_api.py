import datetime
import json
import time
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from mainsite.consumers import send_inform
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import generics
from mainsite.models import mainsite_models
from mainsite.models.mainsite_models import Information
from ..models.notes_models import Note, Note_criticism, Note_reply
from django_redis import get_redis_connection
from notes.models.signals import notes_praise, notes_reply_post, notes_msg_post
from notes import moderation

import logging

notes_log = logging.getLogger('notes_')

common_log = logging.getLogger('django')


def get_func_name(func_name):
    return func_name

def get_headImage(user):
    head_image = user.user.get_headImage
    return '/media/'+str(head_image)

class SignalDetails:
    """the base class for signal information"""

    def general_details(self, author, article, date, trigger, func, slug):
        """the base of information"""
        details = {
            'receiver_username': author,
            'trigger_username': trigger,
            'func': func,
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'article': article,
            'slug': slug,
        }
        return details

    def set_praise_details(self, author, article, date, trigger, func, slug, **kwargs):
        """set the information required for the signal---praise"""
        general = getattr(self, 'general_details')
        details = general(author, article, date, trigger, func, slug)
        if kwargs:
            details.update(**kwargs)
        return details

    def set_msg_details(self, author, article, date, trigger, func, slug, **kwargs):
        """set the information required for the signal---message"""
        general = getattr(self, 'general_details')
        details = general(author, article, date, trigger, func, slug)
        if kwargs:
            details.update(**kwargs)
        return details

    def set_reply_details(self, author, article, date, trigger, func, slug, **kwargs):
        """set the information required for the signal---reply"""
        general = getattr(self, 'general_details')
        details = general(author, article, date, trigger, func, slug)
        if kwargs:
            details.update(**kwargs)
        return details


class notes_statistic_api(APIView):
    """
    笔记统计api类视图
    """

    def get(self, request):
        """
        处理get方法
        :param request:
        :return:返回笔记的统计情况
        """
        all_notes_counts = len(Note.note_.all())  # 笔记总数量
        all_notes = Note.note_.all()
        # all_notes_praise = reduce(lambda x, y: x + y, [note.praise for note in all_notes])  # 笔记总点赞数
        all_notes_praise = sum([note.praise for note in all_notes])  # 内置方法比reduce效率更高一点
        all_notes_visit = 0
        for all_visit in all_notes:
            all_notes_visit += all_visit.read_counts
        data = {
            'all_notes_counts': all_notes_counts,
            'all_notes_praise': all_notes_praise,
            'all_notes_visit': all_notes_visit,
        }
        return JsonResponse(data)


class note_http_serializers(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['title', 'slug', 'praise', 'note_author', 'read_counts', 'publish_date']


class Add_grade(APIView):
    """
        处理post请求,增加点赞数
        :param request:
        :return:成功处理状态
        """
    signal_details = SignalDetails()

    def post(self, request):
        status = request.POST.get('praise_status')
        title = request.POST.get('title')
        author = request.POST.get('author')
        note = Note.note_.get(title=title)
        is_login = True if request.user.is_authenticated else False  # request.user 中间件的属性
        praise_counts = note.praise
        if status == 'Yes':
            praise_counts += 1
            Note.note_.filter(title=title).update(praise=praise_counts)
        data = {
            'status': 'success',
            'praise_counts': praise_counts,
        }
        praise_details = getattr(self.signal_details, 'set_praise_details')
        signal_praise_details = praise_details(author, title, date=datetime.datetime.now(), trigger=request.user.get_username(),
                                               func=get_func_name('praise'),slug=note.slug)
        # send the signal to the callback
        notes_praise.send(
            sender=Note,
            request=request,
            signal_praise_details=signal_praise_details,
        )
        if is_login:
            head_image = get_headImage(request.user)
            praise_username = request.user.get_username()
        else:
            head_image = 'https://django-blog-syz.oss-cn-shanghai.aliyuncs.com/u%3D2471723103%2C4261647594%26fm%3D26%26gp%3D0.jfif'
            praise_username = '一名游客'
        send_inform('praise', author, title, note.slug,head_image, praise_username)
        return JsonResponse(data)

class note_list(APIView):  # APIView而不用View
    """
    notes列表统计http类视图
    """

    def get(self, request):
        """
        处理get对象，返回每篇笔记具体的信息
        :param request:
        :return:resful数据
        """
        note = Note.note_.all().order_by('-read_counts')[:5]
        serializer = note_http_serializers(note, many=True)
        return Response(serializer.data)


class search_serializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['title', 'slug']


@csrf_exempt  # 为了便于跨域访问，取消当前函数防跨站请求伪造功能
def modify_Note_criticism_times(request):
    """
    数据库修改点赞数据
    :return:
    """
    data = {
        'status': 'success'
    }
    try:
        if request.POST.get('function') == 'criticism':
            msg_id = request.POST.get('msg_id')
            # 没有请求到返回None
            if request.POST.get('praise_counts'):
                praise_times = request.POST.get('praise_counts')
                Note_criticism.Note_criticism_.filter(id=msg_id).update(praise_counts=praise_times)
            if request.POST.get('tread_counts'):
                npraise_times = request.POST.get('tread_counts')
                Note_criticism.Note_criticism_.filter(id=msg_id).update(tread_counts=npraise_times)
            return JsonResponse(data)
        elif request.POST.get('function') == 'reply':
            msg_id = request.POST.get('msg_id')
            if request.POST.get('praise_counts'):
                praise_times = request.POST.get('praise_counts')
                Note_reply.Note_reply_.filter(id=msg_id).update(praise_counts=praise_times)
            if request.POST.get('tread_counts'):
                npraise_times = request.POST.get('tread_counts')
                Note_reply.Note_reply_.filter(id=msg_id).update(tread_counts=npraise_times)
            return JsonResponse(data)
    except Exception as e:
        data['status'] = 'error'
        return JsonResponse(data)


class Write_note_criticism(APIView):
    """
    笔记写评论
    :param request:Request对象
    :return:
    """
    signal_details = SignalDetails()

    def post(self, request):
        try:
            criticism = request.POST.get('write_criticism')
            slug = request.POST.get('slug')
            author = request.POST.get('author')
            title = request.POST.get('title')  # 文章的标题
            note = Note.note_.get(slug=slug)
            date = datetime.datetime.now()
            user = User.objects.get(username=request.user.get_username())
            new_criticism = Note_criticism.Note_criticism_.create(
                criticism_content=criticism,
                dates=date,
                criticism_author=user.user,
                note_slug=note
            )
            # values_list返回固定字段的元祖，flat=True转为列表，values()返回字典格式，没有flat属性
            new_msgs = {
                'criticism_id': new_criticism.id,  # 用来点赞ajax请求修改对应的msg
                'criticism_content': criticism,
                'date': date,
                'head_image': get_headImage(user),
                'criticism_author': user.get_username(),
                'status': 'success',
            }

            set_msg_details = getattr(self.signal_details, 'set_msg_details')
            signal_notes_msg = set_msg_details(author, title, date=date, trigger=user.get_username(),
                                               func=get_func_name('msg'), slug=slug)
            # send the signal to the callback
            notes_msg_post.send(
                sender=Note_criticism,
                request=request,
                signal_notes_msg=signal_notes_msg,
                created=True,
            )
            head_image = get_headImage(user)
            send_inform('msg', author, title, slug, head_image, request.user.get_username())
            return JsonResponse(new_msgs)

        except Exception as e:
            notes_log.error(str(e))
            new_msgs = {
                'status': 'error'
            }
            return JsonResponse(new_msgs)



class Write_note_reply(APIView):
    """
    写回复
    :param request: Request对象
    :return: JsonResponse对象
    """
    signal_details = SignalDetails()

    def set_signal_details(self, author, func, article):
        """set the information required for the signal about reply"""
        signal = {
            'receiver_username': author,
            'func': func,
            'time': datetime.datetime.now(),
            'article': article
        }
        return signal

    def post(self, request):
        try:
            reply_content = request.POST.get('reply_content')
            msg_id = request.POST.get('msg_id')  # 对应回复的msg
            author = request.POST.get('author')
            title = request.POST.get('title')
            slug = request.POST.get('slug')
            date = datetime.datetime.now()
            msg = Note_criticism.Note_criticism_.get(id=msg_id)
            user = User.objects.get(username=request.user.username)
            msg_reply = Note_reply.Note_reply_.create(
                note_criticism=msg,
                reply_author=user.user,
                dates=date,
                reply_content=reply_content
            )
            new_reply = {
                # 可以通过回复对象的id号寻找相应位置，但前端可以简化，直接聚焦于添加到回复按钮上方，因此没必要
                'reply_id': msg_reply.id,  # 用来点赞ajax请求修改对应的reply
                'reply_content': reply_content,
                'date': date,
                'head_image': get_headImage(user),
                'reply_author': user.get_username(),
                'status': 'success',
            }

            set_reply_details = getattr(self.signal_details, 'set_reply_details')
            signal_notes_reply = set_reply_details(author, title, date=date, trigger=user.get_username(),
                                                   func=get_func_name('reply'),slug=slug)
            # send the signal to the callback
            notes_reply_post.send(
                sender=Note_reply,
                request=request,
                signal_notes_reply=signal_notes_reply,
                created=True,
            )
            head_image = get_headImage(user)
            common_log.info(head_image)
            send_inform('reply', author, title, slug, head_image, request.user.get_username())
            return JsonResponse(new_reply)
        except Exception as e:
            notes_log.error(str(e))
            new_msgs = {
                'status': 'error'
            }
            return JsonResponse(new_msgs)


class Recent_reply(APIView):
    """笔记更新消息提醒"""

    redis = None
    # 　可能造成　信号重复

    assert hasattr(moderation, 'moderator'), (
        'You should instantiate this class to enable signal listening'
    )
    _moderator = getattr(moderation, 'moderator')

    customize_hashtable_name = _moderator.customize_hashtable_name
    customize_value = _moderator.customize_value

    def get_redis(self, db=None):
        assert db, (
            'db should be determined,Setting "default" if  you want to use the default database'
        )
        self.redis = get_redis_connection(db)

    '''
    def customize_hashtable_name(self,receiver_username,func):
        """hook for Gets the custom hash table"""
        return "%s-%s" % (receiver_username, func)

    def customize_value(self,trigger_username,article):
        """hook for Gets the custom value"""
        return "%s-%s" % (trigger_username, article)
    '''

    def parse_hashtable_name(self, hashtable):
        """解析hash表名"""
        # 解码
        table_list = hashtable.decode().split('-')
        func = table_list.pop()
        receiver_username = table_list.pop()
        return (receiver_username, func)

    def parse_value(self, value):
        """解析值"""
        # 解码
        value_list = value.decode().split('-')
        article = value_list.pop()
        trigger_username = value_list.pop()
        return (article, trigger_username)

    def prefix_url(self,slug):
        """获取url全路径"""
        return '/notes/user_articles_list/'+slug

    def custom_message(self, trigger_username, time, article, func_name, slug):
        """自定义消息格式"""
        global message
        if func_name == 'praise':
            message = '{username}   在   {time}  给您的文章<a href="{slug}">《{article}》点了个大写的赞！</a>赶紧去看看吧~'.format(
                username=trigger_username,
                time=time,
                slug=self.prefix_url(slug),
                article=article
            )
        elif func_name == 'msg':
            message = '{username}   在  {time}  <a href="{slug}">评论了您文章《{article}》！</a>赶紧去看看吧~'.format(
                username=trigger_username,
                time=time,
                slug=self.prefix_url(slug),
                article=article
            )
        elif func_name == 'reply':
            message = '{username}   在   {time}  在文章<a href="{slug}">《{article}》中回复了您的评论！</a>赶紧去看看吧~'.format(
                username=trigger_username,
                time=time,
                slug=self.prefix_url(slug),
                article=article
            )
        return message

    def get_response_data(self, message, index, readStatus):
        """设置前端接收格式"""
        return {
            'text': message,
            'id': index,
            'readStatus': int(readStatus)
        }

    def deserialization(self, sequences, func_name):
        """反序列化"""
        # 值类型：trigger_username-article-status
        global response_data
        serializers = []
        index = 1
        assert hasattr(self, 'get_response_data'), (
                'The method %s should be used to get the data needed for the front end'
                % 'get_response_data'
        )
        response_data = getattr(self, 'get_response_data')
        for key, value in sequences.items():
            time = key.decode()
            value_list = value.decode().split('~')
            status = value_list.pop()  # 消息阅读状态
            slug = value_list.pop()  # 获取每篇文章的slug
            article = value_list.pop()
            trigger_username = value_list.pop()
            message = self.custom_message(trigger_username, time, article, func_name, slug)
            data = response_data(message, index, status)
            serializers.append(data)
            index = index + 1
        return serializers

    def get_hashtable_length(self, hashtable):
        """获取对应hashtable的键值长度"""
        return self.redis.hlen(hashtable)

    def general_get_signal_information(self, username, func_name):
        """通用方法来获取redis中有关笔记操作的信号消息"""
        hashtable = self.customize_hashtable_name(username, func_name)
        inform_number = self.get_hashtable_length(hashtable)
        sequences = self.redis.hgetall(hashtable)
        message = self.deserialization(sequences, func_name)
        return message, inform_number

    def get_note_msg(self, username, func_name=None):
        """获取redis中最新的笔记评论信号信息"""
        if not func_name:
            func_name = get_func_name('msg')
        msg_message, msg_inform_number = self.general_get_signal_information(username, func_name)
        return msg_message, msg_inform_number

    def get_note_reply(self, username, func_name=None):
        """获取redis中最新的笔记回复信号信息"""
        if not func_name:
            func_name = get_func_name('reply')
        reply_message, reply_inform_number = self.general_get_signal_information(username, func_name)
        return reply_message, reply_inform_number

    def get_note_add(self, username, func_name=None):
        """获取redis中最新的笔记添加信号信息"""
        hashtable = self.customize_hashtable_name(username, func_name)
        inform_number = self.get_hashtable_length(hashtable)
        pass

    def get_note_praise(self, username, func_name=None):
        """获取redis中最新的笔记点赞信号信息"""
        if not func_name:
            func_name = get_func_name('praise')
        praise_message, praise_inform_number = self.general_get_signal_information(username, func_name)
        return praise_message, praise_inform_number

    def get(self, request):
        return HttpResponse('555')

    def post(self, request):
        try:
            username = request.POST.get('username')
            receiver_username = request.user.get_username()
            if username != receiver_username:
                result = {
                    'status': 'error',
                    'msg': 'no message',
                }
                return JsonResponse(result)
            else:
                self.get_redis('default')  # 实例化redis
                praise_message, praise_inform_number = self.get_note_praise(receiver_username)
                msg_message, msg_inform_number = self.get_note_msg(receiver_username)
                reply_message, reply_inform_number = self.get_note_reply(receiver_username)
                total_inform_number = praise_inform_number + msg_inform_number + reply_inform_number
                praise_message.extend(msg_message)
                reply_message.extend(praise_message)
                result = {
                    'status': 'success',
                    'msg': 'have message',
                    'datas': reply_message,
                    'totalNumber': total_inform_number,
                }
                return JsonResponse(result)
        except Exception as e:
            notes_log.error(str(e))
            raise Http404
