from django.contrib.auth.models import User
from django.db import models
from mainsite.models.mainsite_models import Information


# Create your models here.
class Message(models.Model):
    """
    留言板数据模型
    """
    message_content = models.TextField(default='请再次输入留言内容', verbose_name='留言')
    dates = models.DateTimeField(auto_now_add=True, verbose_name='日期')
    praise_counts = models.IntegerField(default=0, verbose_name='点赞量', help_text='这里会自动登记，请不要改')
    tread_counts = models.IntegerField(default=0, verbose_name='差评量', help_text='这里会自动登记，请不要改')
    times = models.CharField(max_length=30, default=0, verbose_name='留言者留言次数', help_text='这里会自动登记，请不要改')  # 留言次数
    msg_author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='留言者',
                                   related_name='msg_author', help_text='请选择自己的账号')
    message_ = models.Manager()

    class Meta:
        ordering = ('-praise_counts',)

    def __str__(self):
        return self.message_content


class Message_reply(models.Model):
    """
    多对一，多个回复对应一条评论
    """
    # 级联删除，只要评论删除，相应的回复全部删除,verbose_name 作为类似字段的说明,下划线自动转化为空格
    # ForeignKey , ManyToManyField ,OneToOneField要显示制定verbose_name,其他字段默认会按字段名生成
    # 相当于自然连接，只不过是谁作为第一筛选条件而已
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='留言',
                                related_name='reply', help_text='请选择针对哪条留言')
    times = models.CharField(max_length=30, default=0, verbose_name='评论次数', help_text='这里会自动登记，请不要改')  # 单挑留言评论次数
    tread_counts = models.IntegerField(default=0, verbose_name='差评量', help_text='这里会自动登记，请不要改')
    praise_counts = models.IntegerField(default=0, verbose_name='点赞量', help_text='这里会自动登记，请不要改')
    # reply_author 为User的外键
    reply_author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='回复者',
                                     related_name='reply_author', help_text='请选择自己的账号')
    dates = models.DateTimeField(auto_now_add=True)  # 数据第一次创建才会保存，才会重写
    reply_content = models.TextField(default='请输入回复内容', verbose_name='回复内容')

    message_reply_ = models.Manager()

    class Meta:
        ordering = ('-dates',)

    def __str__(self):
        return self.reply_content
