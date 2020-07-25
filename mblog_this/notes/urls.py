from django.urls import path, include
from django.views.decorators.cache import cache_page

from notes.views import notes, dispaly_articles, note_search

app_name = 'notes'

user_note = ([
                 # 不需要登录
                 path('note/<str:type_>/page_number=<int:page_number>/', notes.get_notes, name='note'),
             ], 'user_note')

user_articles_list = ([
                     # 不需要登录
                     path('<slug:slug>/', dispaly_articles.get_article, name='articles'),
                 ], 'user_articles_list')

urlpatterns = [
    # 不需要登录
    path('user_note/', include(user_note), name='user_note'),
    path('user_articles_list/', include(user_articles_list), name='user_articles_list'),
]
