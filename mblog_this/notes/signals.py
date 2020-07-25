from django.dispatch import Signal

# 用于对文章点赞的信号

notes_praise = Signal(providing_args=["request", "signal_praise_details"])

# 用于文章增添评论的信号

notes_msg_post = Signal(providing_args=["request", "signal_notes_msg", "created"])

# 用于评论增添回复的信号

notes_reply_post = Signal(providing_args=["request", "signal_notes_reply", "created"])

# 用于增加文章的信号

notes_add = Signal(providing_args=["signal_notes_created", "created"])
