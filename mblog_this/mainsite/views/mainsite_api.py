import datetime
import logging
from abc import ABC
from collections import Counter
from functools import reduce
from operator import itemgetter

from comment.models.comment_models import Message
from django.contrib.auth import login
from django.contrib.auth.models import User, Permission
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from mainsite.models.mainsite_models import Information, IPs
from mainsite.tasks import set_verification_code, send_verification
from notes.models import notes_models
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from xadmins.rewrite_auth_user import EmailBackend

logger = logging.getLogger('mainsite_logins')
logging.basicConfig(filename='mainsite/info_login.log', level=logging.INFO,
                    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')


class msg_serializers(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('message', 'msg_author', 'praise_counts', 'tread_counts')
        read_only_fields = ['msg_author', ]


common_log = logging.getLogger('django')

@api_view(['GET'])  # 用于dispatch()HTTP请求的方法
def msg_times_api(request):
    """
    获取点赞量 api
    :param request:请求对象
    :return:
    """
    global msg
    try:
        if request.method == 'GET':
            msg = Message.message_.all()
            serializer = msg_serializers(msg, many=True)
            return Response(serializer.data)
        else:
            pass
    except msg.DoesNotExist:
        raise Http404("Msg Does Not Exist")


class msg_statistic_serializers(serializers.ModelSerializer):
    """
    后期修改成api方式传递数据
    """
    pass


@api_view(['GET'])
def msg_statistic_api(request):
    """
    留言板统计 api
    :param request:请求对象
    :return:
    """
    global msgs
    try:
        if request.method == 'GET':
            msgs = Message.message_.all()
            msg_counts = len(msgs)
            praise_counts = reduce(lambda x, y: x + y, [msg.praise_counts for msg in msgs])
            tread_counts = reduce(lambda x, y: x + y, [msg.tread_counts for msg in msgs])
            pass
    except msgs.DoesNotExist:
        raise Http404("Msgs Does Not Exist")


def add_permissions(user):
    """设置所有用户基本的权限"""
    # 删选基本权限

    permissions = [
        'add_message',
        'change_message',
        'delete_message',
        'view_message',
        'add_message_reply',
        'change_message_reply',
        'delete_message_reply',
        'view_message_reply',
        'add_information',
        'change_information',
        'delete_information',
        'view_information',
        'add_ips',
        'change_ips',
        'delete_ips',
        'view_ips',
        'add_note',
        'change_note',
        'delete_note',
        'view_note',
        'add_note_criticism',
        'change_note_criticism',
        'delete_note_criticism',
        'view_note_criticism',
        'add_note_reply',
        'change_note_reply',
        'delete_note_reply',
        'view_note_reply',
        'add_lagou',
        'change_lagou',
        'delete_lagou',
        'view_lagou',
        'publish_article',
        'draft_article',
    ]

    pers = Permission.objects.filter(codename__in=permissions)
    for per in pers:
        user.user_permissions.add(per)


class login_windows(APIView):
    """
    窗体登录、注册验证
    """

    def post(self, request):
        """
        处理post请求
        :param request:Request的对象
        :return:处理成功或失败JSON数据
        """
        # data相比于get和post可以处理json，而post只能处理字典类型的数据
        IP_ = request.META.get('REMOTE_ADDR', 'unknown')  # 获取ip地址
        time = datetime.datetime.now().strftime('%Y{y}%m{m}-%d{d}-%H-%M-%S').format(y='年', m='月', d='日')  # 获取当前时间
        user_id = request.data.get('user_id').strip()  # 邮箱
        user_password = request.data.get('user_password').strip()
        function = request.data.get('function')  # 功能
        emailBackend = EmailBackend()  # 生成认证实例
        result = {
            'code': 0,
            'msg': '',
            'status': ''
        }
        # 登录post
        if function == 'login':
            # authenticate用来表示后端验证了该用户，经过认证，返回一个user对象
            user_auth = emailBackend.authenticate(request, username=user_id, password=user_password)
            login_status = True if user_auth else False
            if login_status:
                login(request, user_auth)  # 登录
                IPs.ip_.create(  # 记录一次ip
                    ips=IP_,
                    time=time,
                    ips_author=user_auth
                )
                result['code'] = 1
                result['status'] = 'success'
                return JsonResponse(result)
            else:
                result['code'] = -1
                result['status'] = 'error'
                return JsonResponse(result)
        # 注册post
        elif function == 'register':
            # logger.info(status)
            user_name = request.POST.get('user_name').strip()  # 用户名
            verification_code = request.POST.get('verification_code')  # 验证码
            verification_code_session = request.session.get('verification_code_register')  # 比对用户验证码
            # 判断验证码和用户详情表中是否存在
            global registered_status
            try:
                # 判断User中是否存在用户
                User.objects.get(email=user_id)
            except User.DoesNotExist:
                registered_status = True
            else:
                registered_status = False
            # 如果验证码不存在
            if verification_code != verification_code_session:
                # 以后改成result['code'] = '-6'
                result['code'] = -6  # 验证码错误
                result['status'] = 'verification_error'  # 验证码错误状态说明
                return JsonResponse(result)
            # 如果满足所有登录要求
            try:
                if registered_status:
                    # 创建普通用户
                    user = User.objects.create_user(username=user_name, email=user_id, password=user_password)
                    Information.information_.create(user=user, motto='', hobby='', head_image='')
                    user.is_active = True  # 判断用户是否激活
                    user.is_staff = True  # 判断用户是否可以进入admin
                    user.save()
                    # 提供认证用户，将该用户标识为已认证，方便之后is_authenticate（）的使用。
                    user_auth = emailBackend.authenticate(request, username=user_id, password=user_password)
                    add_permissions(user_auth)  # 增加权限
                    # login函数主要将session_id写到cookie发送给前端
                    login(request, user_auth, backend=emailBackend)  # 登录
                    IPs.ip_.create(  # 记录一次ip
                        ips=IP_,
                        time=time,
                        ips_author=user_auth
                    )
                    result['code'] = 26  # 注册成功，验证码正确
                    result['status'] = 'success'
                    return JsonResponse(result)
                else:
                    result['code'] = -26  # 注册失败
                    result['status'] = 'error'
                    return JsonResponse(result)
            except Exception as e:
                raise Http404


class Information_related(serializers.RelatedField, ABC):
    """自定义用于处理Information的字段"""

    def to_representation(self, value):
        pass


class Information_serializer(serializers.ModelSerializer):
    # 通过source获取user中的username属性
    user = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Information
        fields = ('user', 'motto', 'hobby', 'head_image', 'email')


class Inforamtions(APIView):
    """
    获取、设置个人信息api
    """

    def get(self, request):
        """
        处理get请求消息
        :return: 返回Response对象
        """
        user = request.user if request.user.is_authenticated else '游客'
        try:
            information = Information.information_.get(user=user)
            serializer = Information_serializer(information)
            return Response(serializer.data)
        except Information.DoesNotExist:
            raise Http404


@csrf_exempt
def modify_information(request):
    """
        修改个人信息
        :param request:
        :return:返回Json  Response对象
        """
    user_email = request.POST.get('user_email').strip()
    user_name = request.POST.get('user_name')
    function = request.POST.get('function')
    data = {
        'code': 0,
        'msg': '',
        'status': ''
    }
    if function == 'modify_head_image':
        head_image = request.FILES.get('head_image')  # 获取文件字段,返回文件对象，以文件名形式
        # ImageField存储的也就是文件名，然后结合media_url来进行访问，同时在media_root下创建文件对象,以后get需要访问media_root下的文件对象
        # 可以不用手动写图片
        '''
            head_images = r'{user_name}_{image_name}'.format(user_name=user_name, image_name=head_image)
            result = Information.information_.filter(email=user_email) \
                .update(head_image=head_images)
            # file_list = os.listdir(MEDIA_ROOT)
            # 这里后期要处理单个用户多余重复的头像
            filename = os.path.join(MEDIA_ROOT, head_images)
            with open(filename, 'wb') as head_F:
                # chunks以块的形式将图片大文件写入文件中，如果文件过大，会占用系统内存，导致变慢，因此分块写更好
                for i in head_image.chunks():
                    head_F.write(i)
            '''
        try:
            user = User.objects.get(email=user_email)
            user.user.head_image = head_image
            user.user.save()
            data['code'] = 5  # 修改头像成功code
            data['status'] = 'success'
            return JsonResponse(data)
        except User.DoesNotExist:
            data['code'] = -5  # 修改头像成功code
            data['status'] = 'error'
            return JsonResponse(data)

    elif function == 'save_information':
        user_motto = request.POST.get('user_motto', default='')
        user_hobby = request.POST.get('user_hobby', default='')
        try:
            user = User.objects.get(email=user_email)
            user.username = user_name
            user.user.motto = user_motto
            user.user.hobby = user_hobby
            user.save()
            user.user.save()
            data['code'] = 4  # 用户修改信息成功code
            data['status'] = 'success'
            return JsonResponse(data)
        except User.DoesNotExist:
            data['code'] = -4  # 用户修改信息成功code
            data['status'] = 'error'
            return JsonResponse(data)


class modify_password(APIView):
    """
    修改密码，发送密码不需要邮箱验证
    """

    def get(self, request):
        """
        处理get请求
        :param request: Request对象
        :return:
        """
        pass

    def post(self, request):
        """
        处理post请求
        :param request: Request对象
        :return:
        """
        function = request.data.get('function')
        data = {
            'code': 0,
            'msg': '',
            'status': 'error',
        }
        user_name = request.session.get('user')
        if function == 'save':
            old_pwd = request.data.get('old_pwd')
            new_pwd = request.data.get('new_pwd')
            verification_code = request.data.get('verification_code')
            if verification_code == request.session.get('verification_code'):
                # update返回0/1
                result = Information.information_.filter(user_name=user_name, user_password=old_pwd).update(
                    user_password=new_pwd)
                if result > 0:
                    data['code'] = 200
                    data['status'] = 'success'
                    return JsonResponse(data)
                return JsonResponse(data)
            data['code'] = 500
            return JsonResponse(data)
        elif function == 'mail':
            verification_code = set_verification_code()
            request.session['verification_code'] = verification_code
            title = '云博博客修改密码'
            content = '尊敬的用户，您修改密码所需的验证码为' + verification_code + '验证码有效期1小时！'
            # 这地方有点小问题，昵称重复取到的邮箱可能有多个用户的，而这里只需要一个邮箱
            user = Information.information_.filter(user_name=user_name)
            try:
                send_verification.delay(title, content, user[0].email)
                data['code'] = 200
                data['status'] = 'success'
                return JsonResponse(data)
            except Exception as e:
                logger.info('send_email_modify_pwd:{}'.format(e))
                return JsonResponse(data)


class email_verification(APIView):
    """
    注册、找回密码发送验证邮件，需要进行邮箱验证
    :return:
    """

    def post(self, request):
        data = {
            'code': 0,
            'msg': '',
            'status': 'error'
        }
        function = request.data.get('function')
        if function == 'find_password':
            verification_code = set_verification_code()
            title = '云博博客找回密码'
            content = '尊敬的用户，已经将云博博客网站的密码重置为：' + verification_code + '使用临时密码登录后，' \
                                                                     '请尽快修改密码,验证码有效期1小时！'
            user_email = request.data.get('email')
            # fail_Silently表示是否忽略邮件发送失败的异常
            try:
                # 邮箱验证,邮箱应该唯一
                result = Information.information_.filter(email=user_email)
                if len(result) == 1:
                    send_verification.delay(title, content, user_email)  # 启动任务
                    data['code'] = 200
                    data['status'] = 'success'
                    result.update(user_password=verification_code)
                    return JsonResponse(data)
                else:
                    logger.info('email DoesNotExist')
                    return JsonResponse(data)
            # 捕捉发送邮件异常
            except Exception as e:
                data['code'] = 500
                logger.info('find_password_send_email_error:{}'.format(e))
                return JsonResponse(data)

        elif function == 'register':
            user_id = request.data.get('user_id').strip()
            verification_code = set_verification_code()
            title = '云博博客用户注册'
            content = '尊敬的用户，欢迎您注册云博博客，您的验证码为：{code},鄙人才疏学浅，仅为记录学习心得，关于博客' \
                      '里的笔记，如有兴趣，可以一起交流学习！验证码有效期1小时!'.format(code=verification_code)
            try:
                # delay中放参数！！！注意启用任务的格式
                send_verification.delay(title, content, user_id)  # 发送成功返回1
                data['code'] = 8
                data['status'] = 'success'
                request.session['verification_code_register'] = verification_code
                return JsonResponse(data)
            # 使用邮件必须要捕捉异常，不然会报错！！！
            except Exception as e:
                data['code'] = -8
                logger.info('register_send_email_error:{}'.format(e))
                return JsonResponse(data)


class contact_syz_api(APIView):
    """
    发送邮件给管理员
    """

    def post(self, request):
        """
        处理post请求
        :return:
        """
        data = {
            'code': 0,
            'msg': '',
            'status': 'error'
        }
        contents = request.POST.get('contents')
        title = '一封来自云博用户的信'
        try:
            send_verification.delay(title, contents, '247179876@qq.com')
            data['code'] = 200
            data['status'] = 'success'
            return JsonResponse(data)
        except Exception as e:
            logger.info(e)
            data['code'] = 500
            return JsonResponse(data)


@api_view(['GET'])
def head_url_api(request):
    """
    获取头像api
    :param request: Request对象
    :return:Response对象
    """
    # 这地方后期修改为唯一键
    user = request.user if request.user.is_authenticated else '游客'
    try:
        information = Information.information_.get(user=user)
        serializer = Information_serializer(information)
        return Response(serializer.data)
    except Information.DoesNotExist:
        raise Http404


class Notes_counts(APIView):

    @staticmethod
    def get_notes_counts():
        """获取各类型的笔记数目"""
        exist_notes = notes_models.Note.note_.filter()
        # result_dict = {}
        # for note in exist_notes:
        #     result_dict[note.type] = result_dict.setdefault(note.type, 0) + 1
        # 字典转转为列表
        result_dict = sorted(Counter((note.type for note in exist_notes)).items(), key=itemgetter(1), reverse=True)
        return result_dict

    def get(self, request):
        """提供不同类型的笔记数目"""
        result_dict = self.get_notes_counts()
        return Response(result_dict)
