# from django.contrib import messages
import datetime
import json
import logging
from collections import UserDict

from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, JsonResponse
from django.template.response import TemplateResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mblog.Json import JsonCustomEncoder
from rest_framework.response import Response
from rest_framework.views import APIView

from comment.models import comment_models
from mainsite.models.mainsite_models import Information

from comment.models.signals import comment_posted, reply_posted

common_log = logging.getLogger('django')
comment_log = logging.getLogger('comment_')


@require_http_methods(['GET', 'POST'])  # 约束请求的方法，请求类型不正确，返回HttpResponseNotAllowed异常错误。
def display_msg(request):
    """
    展示留言版
    :return:
    """
    # 采用主存cache实现缓存
    '''result = cache.get('msg')
    if result:
        return JsonResponse(result)
    else:
        data = models.Message.message_.all()
        c_Data = []
        for i in data:
            c_Data.append(model_to_dict(i))
        results = {'msg': c_Data}
        cache.set('msg', results, 30)
        return JsonResponse(results)
    '''
    # 采用Memcached实现缓存
    # user = request.session.get('user', default='游客')
    user = request.user
    display_msgs = comment_models.Message.message_.all()
    msgs = {}
    for msg in display_msgs:
        msgs[msg.id] = {
            'msg_message': msg.message_content,
            'msg_date': msg.dates,
            'msg_praise_counts': msg.praise_counts,
            'msg_tread_counts': msg.tread_counts,
            'msg_author_name': msg.msg_author.username,
            'msg_author_head_image': '/media/{filename}'.format(filename=str(msg.msg_author.user.head_image)),
            'replys': [],
        }
        for reply in msg.reply.all():
            replys = {
                'reply_id': reply.id,
                'reply_head_image': '/media/{filename}'.format(filename=str(reply.reply_author.user.head_image)),
                'reply_tread_counts': reply.tread_counts,
                'reply_praise_counts': reply.praise_counts,
                'reply_author': reply.reply_author.username,
                'reply_dates': reply.dates,
                'reply_content': reply.reply_content,
            }
            msgs[msg.id]['replys'].append(replys)
    response = TemplateResponse(request, 'message_board.html', locals())
    return response.render()  # 可以注册回调函数


def write_msg(request):
    """
    写留言
    :param request:Request对象
    :return:
    """
    try:
        message_content = request.POST.get('write_message')
        user = request.user
        # request.user和 User.objects.get(username=request.user.username)返回值对象不同哦
        date = datetime.datetime.now()
        new_msg = comment_models.Message.message_.create(
            message_content=message_content,
            dates=date,
            msg_author=user,
        )
        # values_list返回固定字段的元祖，flat=True转为列表，values()返回字典格式，没有flat属性
        # new_message = models.Message.message_.filter(msg_author.user_name=user)
        # times = user.values_list('times', flat=True)[0]

        new_msg = {
            'msg_id': new_msg.id,
            'msg_content': message_content,
            'date': date,
            'head_image': '/media/{filename}'.format(filename=str(user.user.head_image)),
            'msg_author': user.username,
            'status': 'success',
        }
        # signal_comment_msg = {
        #     'msg_author': user.username,
        #     'date': date,
        #     'fuc': 'message'
        # }
        # m = comment_posted.send(
        #     sender=comment_models.Message,  # 对应的类
        #     request=request,
        #     signal_comment_msg=signal_comment_msg,
        #     created=True,
        # )
        return JsonResponse(new_msg)
    except Exception as e:
        new_msg = {
            'status': 'error'
        }
        return JsonResponse(new_msg)


def write_reply(request):
    """
    写回复
    :param request: Request对象
    :return: JsonResponse对象
    """
    try:
        reply_content = request.POST.get('reply_content')
        msg_id = request.POST.get('msg_id')  # 对应回复的msg
        date = datetime.datetime.now()
        msg = comment_models.Message.message_.get(id=msg_id)
        user = request.user
        msg_reply = comment_models.Message_reply.message_reply_.create(
            message=msg,
            reply_author=user,
            dates=date,
            reply_content=reply_content
        )
        new_reply = {
            # 可以通过回复对象的id号寻找相应位置，但前端可以简化，直接聚焦于添加到回复按钮上方，因此没必要
            'reply_id': msg_reply.id,  # 用来点赞ajax请求修改对应的reply
            'reply_content': reply_content,
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'head_image': '/media/{filename}'.format(filename=str(user.user.get_headImage)),
            'reply_author': user.username,
            'status': 'success',
        }

        # signal_comment_reply = {
        #     'receiver_user': msg.msg_author,
        #     'reply_author': user.username,
        #     'date': date,
        #     'func': 'reply'
        # }
        # reply_posted.send(
        #     sender=comment_models.Message_reply,
        #     request=request,
        #     signal_comment_reply=signal_comment_reply,
        #     created=True,
        # )
        return JsonResponse(new_reply)
    except Exception as e:
        common_log.info(e)
        new_msgs = {
            'status': 'error'
        }
        return JsonResponse(new_msgs)


# @api_view(['POST', 'GET'])  # 用到序列化的
@csrf_exempt  # 为了便于跨域访问，取消当前函数防跨站请求伪造功能
def modify_msg_times(request):
    """
    数据库修改点赞数据
    :return:
    """
    data = {
        'status': 'success'
    }
    msg_id = request.POST.get('msg_id')
    try:
        if request.POST.get('function') == 'msg':
            # 没有请求到返回None
            if request.POST.get('praise_counts'):
                praise_times = request.POST.get('praise_counts')
                comment_models.Message.message_.filter(id=msg_id).update(praise_counts=praise_times)
            if request.POST.get('tread_counts'):
                npraise_times = request.POST.get('tread_counts')
                print(npraise_times)
                comment_models.Message.message_.filter(id=msg_id).update(tread_counts=npraise_times)
            return JsonResponse(data)
        elif request.POST.get('function') == 'reply':
            if request.POST.get('praise_counts'):
                praise_times = request.POST.get('praise_counts')
                comment_models.Message_reply.message_reply_.filter(id=msg_id).update(praise_counts=praise_times)
            if request.POST.get('tread_counts'):
                npraise_times = request.POST.get('tread_counts')
                print(npraise_times)
                comment_models.Message_reply.message_reply_.filter(id=msg_id).update(tread_counts=npraise_times)
            return JsonResponse(data)
    except Exception as e:
        data['status'] = 'error'
        return JsonResponse(data)
