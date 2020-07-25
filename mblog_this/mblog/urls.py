"""mblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.decorators.cache import cache_page
from mainsite.views import mainsite_api
from mainsite.views import mainsite_views
from mblog import settings
from notes.views import notes_api
from visualize.views import visualize_api
from notes.search_indexes import MySearch
from inform.views.inform_api import InformOperation

# register_converter(views.Test, 'yyyy')  # 自定义路由转换器

user_api = ([
                path('inform-latest-api/', InformOperation.as_view(), name='inform-latest-news-api/'),
                path('msg_api/', mainsite_api.msg_times_api, name='msg_api'),  # get
                path('notes_statistic_api/', cache_page(60*30)(notes_api.notes_statistic_api.as_view()), name='notes_statistic_api'),
                # post
                path('add_grade/', notes_api.Add_grade.as_view(), name='add_grade'),  # 点赞
                path('note_list/', cache_page(60*30)(notes_api.note_list.as_view()), name='note_list'),  # get,post
                # path('notes_search_api/', notes_api.notes_search.as_view(), name='notes_search_api'),
                path('visualize_lagou_api/', visualize_api.lagou_table_api, name='visualize_lagou_api'),
                # path('test_api/', visualize_api.test.as_view(), name='test_api'),
                path('information_api/', mainsite_api.Inforamtions.as_view(), name='information_api'),
                path('modify_information_api/', mainsite_api.modify_information, name='modify_information'),
                # path('modify_pwd_api/', mainsite_api.modify_password.as_view(), name='modify_pwd_apo'),
                path('verification_email_api/', mainsite_api.email_verification.as_view(),
                     name='verification_email_api'),
                path('contact_syz_api/', mainsite_api.contact_syz_api.as_view(), name='contact_syz_api'),
                path('head_url_api/', mainsite_api.head_url_api, name='contact_syz_api'),
                path('write_criticism_api/', notes_api.Write_note_criticism.as_view(), name='write_criticism_api'),
                path('write_reply_note_api/', notes_api.Write_note_reply.as_view(), name='write_reply_note_api'),
                path('modify_Note_criticism_times/', notes_api.modify_Note_criticism_times,
                     name='modify_Note_criticism_times'),
                path('recent-notes/', notes_api.Recent_reply.as_view(), name='recent-notes'),
            ], 'user_api')

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls, name='admin'),
    # path('captcha/', include('captcha.urls')),
    path('', mainsite_views.introduce, name='syz_introduce'),
    path('home_page/', mainsite_views.homepage, name='home_page'),
    path('mdeditor/', include('mdeditor.urls')),
    path('mainsite/', include('mainsite.urls')),
    path('notes/', include('notes.urls')),
    path('comment/', include('comment.urls')),
    path('visualize/', include('visualize.urls')),
    path('inform/', include('inform.urls')),
    path('user_api/', include(user_api)),
    path('error_404/', mainsite_views.error_404),
    # 默认使用的HTML模板路径为templates/search/search.html
    path('search/', MySearch(), name='search'),
    path('duplicate/', include('duplicate_checking.urls'))
    # path('test_celery/',include(test_celery)),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # 存放media资源
