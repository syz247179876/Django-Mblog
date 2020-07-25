import datetime

from django.utils.translation import gettext as _
from comment.exceptions import NotRedis, NotCreated
from notes.models import signals, notes_models
import notes
from django_redis import get_redis_connection
import logging

note_log = logging.getLogger('notes_')
common_log = logging.getLogger('django')


class ModeratorBase:
    """Note signal regulator"""

    def __init__(self):
        """setup the connect and acquire the instance of redis"""
        self.connect()
        self._redis = get_redis_connection('default')

    @property
    def redis(self):
        """Get the instance of redis"""
        return self._redis

    @property
    def expire_time(self):
        """set the expire time of a key"""
        return 60 * 60 * 24 * 15

    def connect(self):
        """register signals"""
        signals.notes_msg_post.connect(self.after_notes_msg_posted, sender=notes_models.Note_criticism)
        signals.notes_praise.connect(self.after_notes_praised, sender=notes_models.Note)
        signals.notes_reply_post.connect(self.after_notes_reply_posted, sender=notes_models.Note_reply)
        signals.notes_add.connect(self.after_note_add, sender=notes_models.Note)

    def customize_hashtable_name(self, receiver_username, func):
        """hook for Gets the custom hash table"""
        return "%s~%s" % (receiver_username, func)

    def customize_value(self, trigger_username, article, slug, status=None):
        """hook for Gets the custom value"""
        return "%s~%s~%s~%d" % (trigger_username, article, slug, 0)

    def after_notes_praised(self, sender, request, signal_praise_details, **kwargs):
        """callback when the comment is triggered"""
        signal_general = getattr(self, 'signal_general')
        result = signal_general(sender, request, signal_praise_details, created=True, **kwargs)
        if result:
            common_log.info('笔记点赞信号发送成功')
        else:
            common_log.info('笔记点赞信号发送失败')

    def after_notes_msg_posted(self, sender, request, signal_notes_msg, created, **kwargs):
        """callback when the note is praised"""
        signal_general = getattr(self, 'signal_general')
        result = signal_general(sender, request, signal_notes_msg, created, **kwargs)
        if result:
            common_log.info('笔记评论信号发送成功')
        else:
            common_log.info('笔记评论信号发送失败')

    def after_notes_reply_posted(self, sender, request, signal_notes_reply, created, **kwargs):
        """callback when the reply is triggered"""
        signal_general = getattr(self, 'signal_general')
        result = signal_general(sender, request, signal_notes_reply, created, **kwargs)
        if result:
            common_log.info('笔记回复信号发送成功')
        else:
            common_log.info('笔记回复信号发送失败')

    def after_note_add(self, sender, signal_notes_created, created, **kwargs):
        """callback when the save() is callback"""
        signal_add = getattr(self, 'signal_add')
        result = signal_add(sender, signal_notes_created, created, **kwargs)
        if result:
            common_log.info('笔记添加信号发送成功')
        else:
            common_log.info('笔记添加信号发送失败')

    def signal_add(self, sender, signal_notes_created, created, **kwargs):
        """the signal of Increasing the note"""
        redis = getattr(self, 'redis', None)
        if not redis:
            raise NotRedis("Failed to instantiate redis！")
        if not created:
            raise NotCreated('created should be set True')
        else:
            try:
                notes_add = signal_notes_created.copy()
                id = notes_add.pop('id')
                # 向redis列表中添加最新的文章id
                redis.lpush('newest_article_id', id)
                redis.hmset(id, notes_add)
                redis.expire(id, self.expire_time)
                return True
            except Exception as e:
                note_log.error(str(e))
                return False

    def signal_general(self, sender, request, signal_details, created, **kwargs):
        """general of signal"""
        redis = getattr(self, 'redis', None)
        if not redis:
            raise NotRedis("Failed to instantiate redis！")
        if not created:
            raise NotCreated('created should be set True')
        else:
            try:
                notes_reply = signal_details.copy()
                receiver_username = notes_reply.pop('receiver_username')
                func = notes_reply.pop('func')
                date = notes_reply.pop('date')
                slug = notes_reply.pop('slug')
                trigger_username = notes_reply.pop('trigger_username')
                article = notes_reply.pop('article')
                customize_hashtable_name = getattr(self, 'customize_hashtable_name')
                hash_table = customize_hashtable_name(receiver_username, func)
                customize_value = getattr(self, 'customize_value')
                value = customize_value(trigger_username, article, slug)  # 自定义值形式
                redis.hset(hash_table, date, value)  # 创建散列表存储
                redis.expire(hash_table, self.expire_time)  # 设置过期时间
                return True
            except Exception as e:
                note_log.error(str(e))
                return False


class Moderator(ModeratorBase):

    def __init__(self, customize_hashtable_name=None, customize_value=None):
        super().__init__()
        if customize_hashtable_name:
            self.customize_hashtable_name = customize_hashtable_name
        if customize_hashtable_name:
            self.customize_value = customize_value


moderator = Moderator()
