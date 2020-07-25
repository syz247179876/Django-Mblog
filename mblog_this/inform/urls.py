# -*- coding: utf-8 -*- 
# @Time : 2020/6/17 10:13 
# @Author : 司云中 
# @File : urls.py 
# @Software: PyCharm


from django.urls import path
from inform.views.inform_api import InformOperation


app_name = 'inform'

urlpatterns = [
    # path('inform-latest-api/', InformOperation.as_view(), name='inform-latest-news-api/'),
]