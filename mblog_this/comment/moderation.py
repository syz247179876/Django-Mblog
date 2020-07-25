import datetime

from comment.exceptions import NotRedis, NotCreated
from django.core.signals import request_finished
from django.dispatch import receiver
from django.utils.translation import gettext as _
from comment.models import signals,comment_models
import comment
from django_redis import get_redis_connection


class Moderator:
    """信号调节器"""

    def __init__(self):
        self.connect()
        self._redis = get_redis_connection('default')

    @property
    def redis(self):
        """获取redis客户端实例"""
        return self._redis

    def connect(self):
        """注册信号函数"""
        message, reply = comment.get_model()
        signals.comment_posted.connect(self.post_save_comment, sender=comment_models.Message)
        signals.reply_posted.connect(self.post_save_reply, sender=comment_models.Message_reply)

    def post_save_comment(self, sender, request, signal_comment_msg, created, **kwargs):
        """留言板评论通知博主"""
        if not hasattr(self, 'redis'):
            raise NotRedis("Failed to instantiate redis！")
        if not created:
            raise NotCreated('created should be set True')
        else:
            redis = getattr(self, 'redis')
            msg_information = signal_comment_msg.copy()
            msg_date = msg_information.pop('date')
            msg_username = msg_information.pop('msg_author')
            redis.incr(msg_username, 1)
            redis.expire(msg_username, 60 * 60 * 24 * 30)
            print('222222')

    def customize_reply_key(self,receiver_user,func):
        """自定义comment存入到redis中的键"""
        return '%s-%s' % (receiver_user,func)

    def customize_reply_value(self,reply_author,reply_date):
        """自定义comment错入redis中的值"""
        return '%s-%s' % (reply_author,reply_date)

    def post_save_reply(self, sender, request, signal_comment_reply, created, **kwargs):
        """回复通知各评论者"""
        if not hasattr(self, 'redis'):
            raise NotRedis("Failed to instantiate redis！")
        if not created:
            raise NotCreated('created should be set True')
        else:
            redis = getattr(self, 'redis')
            reply_information = signal_comment_reply.copy()
            reply_date = reply_information.pop('date')
            reply_author = reply_information.pop('reply_author')
            receiver_user = reply_information.pop('receiver_user')
            reply_key_get = getattr(self, 'customize_reply_key')
            func = reply_information.pop('func')
            redis.lpush(reply_key_get(receiver_user, func), reply_date)


'''
@receiver(request_finished)
def my_callback(sender, **kwargs):
    print("Request finished!")
'''

moderator = Moderator()