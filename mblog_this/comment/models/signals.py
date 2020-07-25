from functools import partial

from django.db.models.utils import make_model_tuple

from django.dispatch import Signal

# 这个用于发表评论时的一个信号,通知博主，providing_args的参数用于send和connect共享

comment_posted = Signal(providing_args=["request","signal_comment_msg","created"])

# 用于回复评论的一个信号，通知各评论者。
reply_posted = Signal(providing_args=["request","signal_comment_reply","created"])


