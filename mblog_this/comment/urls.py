from django.urls import path, include

from comment.views import message_board

app_name = 'comment'
user_massage = ([
                    # 登录或者不登录，后期改为登录
                    path('message_board/', message_board.display_msg, name='message_board'),  # 留言板，从此开始！！！代码要写的优雅
                    path('write_message/', message_board.write_msg, name='write_message'),
                    path('modify_msg_times/', message_board.modify_msg_times, name='modify_msg_times'),
                    path('write_reply/', message_board.write_reply, name='write_reply')
                ], 'user_msg')

urlpatterns = [
    path('user_msg/', include(user_massage), name='user_msg'),

]