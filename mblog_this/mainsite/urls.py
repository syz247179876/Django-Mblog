from django.urls import path
from django.views.decorators.cache import cache_page

from mainsite.views import mainsite_views, mainsite_api

app_name = 'mainsite'

urlpatterns = [
    path('register/', mainsite_views.register, name='register'),
    path('login/', mainsite_views.login, name='login'),  # 进入登录页
    # path('login_to_home_page/', views.login_page, name='login_to_home_page'),
    path('logout/', mainsite_views.logout_blog, name='logout'),  # 登出
    path('individual/', mainsite_views.modify_infor, name='individual'),
    path('login_windows/', mainsite_api.login_windows.as_view(),
         name='login_windows'),
    path('basic_information/', mainsite_views.basic_information,
         name='basic_information'),
    # path('find_password/', mainsite_views.find_password, name='find_password'),
    # path('modify_password/', mainsite_views.modify_password,
    # name='modify_password'),
    path('contact_syz/', mainsite_views.contact_syz, name='contact_syz'),
    path('notes-type-counts/', cache_page(60*30)(mainsite_api.Notes_counts.as_view()), name='notes-type-counts'),
    # path('inform-news/', mainsite_api.Notes_counts.as_view(), name='inform-news'),
]  # 使用命名空间进行管理
