# -*- coding: utf-8 -*-

import datetime
import random

import markdown
from django.contrib.auth import logout
from django.http import *
from django.shortcuts import render, redirect
from mainsite.tasks import get_word_cloud, update_daily_note
from notes.models import notes_models
import logging

common_logger = logging.getLogger('django')

error_logger = logging.getLogger('mainsite_')


# Create your views here.


def random_id():
    """随机生成游客id"""
    default_name = ''.join(str(random.randint(1, 9)) for _ in range(10))
    return default_name


def introduce(request):
    """
    个人介绍页
    :param request:HttpRequest对象
    :return: 定向到个人介绍页面
    """
    # user = request.session.get('user', default='游客')
    # request.user.is_authenticated是一个方法
    user = request.user.username if request.user.is_authenticated else '游客'
    my_introduce = notes_models.Note.note_.get(title='个人简介')
    my_introduce.note_contents = markdown.markdown(my_introduce.note_contents, extensions=[
        'markdown.extensions.extra',  # 一些额外的组件
        'markdown.extensions.attr_list',
        'markdown.extensions.smarty',
        'markdown.extensions.codehilite',  # 语法高亮拓展
        'markdown.extensions.toc',  # 自动生成目录
    ], safe_mode=True)
    data = {
        'user': user,
        'introduce': my_introduce,
    }
    # 如果第一次访问这里的话，django会自动生成cookie
    # {'csrftoken':'3KV1lSv2JqMVxTOtq1YNiUh8OjmhwACqoyCdSxwgCAcIK6NWWIozg1WtiMN4zfXL'}
    # 伴随着Httpresponse对象返回给客户端浏览器
    # 如果在这里创建了session,那么django也会生成一条session数据，并将session_id一同作为cookie返回给客户端
    return render(request, 'Introduce.html', data)


def get_cloud():
    """爱好词云图"""
    word_cloud = get_word_cloud.delay().get()
    return word_cloud


def get_daily_notes():
    """笔记日统计图"""
    daily_notes = update_daily_note.delay().get()
    return daily_notes


# 增添缓存1天
# @cache_page(60*60*24)
def homepage(request):
    """主页"""
    try:
        global all_notes_praise
        # IP = request.META.get('REMOTE_ADDR', 'unknown')
        # time = datetime.datetime.now().strftime('%Y{y}%m{m}-%d{d}-%H-%M-%S').format(y='年', m='月', d='日')
        date = datetime.datetime.now()
        recent_date = datetime.timedelta(days=-7)
        past_date = (date + recent_date).strftime('%Y-%m-%d')
        recent_notes = notes_models.Note.note_.filter(publish_date__gte=past_date, status='Published')[:7]
        # 替换为auth的认证is_authenticated()
        user = request.user.username if request.user.is_authenticated else '游客'
        word_cloud = get_cloud()
        daily_notes = get_daily_notes()
        data = {
            'user': user,
            'word_cloud': word_cloud,
            'recent_notes': recent_notes,
            'daily_notes': daily_notes,
        }
        return render(request, 'Index.html', data)
    except Exception as e:
        error_logger.error(str(e))
        return HttpResponse(e)


def register(request):
    """
    注册用户
    :param request:
    :return: 进入注册页
    """
    next_url = request.GET.get('next', None)
    if next_url:
        request.session['next_url'] = next_url
    return render(request, 'Register.html')


def login(request):
    """
    进入登录页
    :param request:
    :return:进入主页
    """
    next_url = request.GET.get('next', None)
    if next_url:
        request.session['next_url'] = next_url
    return render(request, 'Login.html')


def modify_password(requset):
    """
    修改密码
    :param requset:
    :return:进入修改密码
    """

    return render(requset, 'Modify_password.html')


def contact_syz(request):
    """
    联系管理员
    :param request:HttpRequest对象
    :return: 进入联系管理员
    """
    return render(request, 'Contact_syz.html')


def basic_information(request):
    """
    进入个人资料面板
    :param request: HttpRequest对象
    :return: 定向
    """
    return render(request, 'Basic_information.html')


def find_password(request):
    """
    进入修改密码面板
    :param request: HttpRequest对象
    :return: 定向
    """
    return render(request, 'Find_password.html')


def logout_blog(request):
    """
    注销功能
    :param request:
    :return:重定向到FirstHead.html
    """
    try:
        '''
        if 'user' in request.session:
            # del request.session['user']  # 删除当前会话数据的session_data字段值,保留session_id
            request.session.delete()  # 删除当前会话的一整条数据,所以用这个比del要减少存储空间消耗,删除记录
            # return render(request, 'index.html', {'user': '游客'})
        '''
        # 清楚该校
        logout(request)
        return redirect('/home_page')
    except Exception:
        return render(request, '404_error.html')


def modify_infor():
    """
    修改个人信息
    :param request:
    :return:无需定向
    """
    pass


def error_404(request):
    return render(request, '404_error.html')


class Test:
    regex = '[0-9]{4}'

    @staticmethod
    def to_python(value):  # 这个方法是当url传递到函数视图的时候，转换成制定类型
        return int(value)

    @staticmethod
    def to_url(value):  # 进行url翻转，当从外界例如ajax定向的url传进来的参数转化为url类型，即类型转换器字符串
        return '%4d' % value
