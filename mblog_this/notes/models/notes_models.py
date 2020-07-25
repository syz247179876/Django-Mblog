import logging

from django.contrib.auth.models import User
from django.db import models
from django.utils.html import format_html
from mainsite.consumers import send_inform
from mdeditor.fields import MDTextField

from mainsite.models.mainsite_models import Information

notes_log = logging.getLogger('notes_')

common_log = logging.getLogger('django')


class Note(models.Model):
    """
    笔记数据模型
    """
    # 后者显示给用户看，前者相当于存入数据库的值
    note_type = (
        ('Python', 'Python'),
        ('Django', 'Django'),
        ('Java', 'Java'),
        ('Scrapy', 'Scrapy'),
        ('Pandas', 'Pandas'),
        ('Numpy', 'Numpy'),
        ('Layui', 'Layui'),
        ('English', 'English'),
        ('machine_learning', 'machine_learning'),
        ('C#', 'C#'),
        ('C++', 'C++'),
        ('Linux', 'Linux'),
        ('Mysql', 'Mysql'),
        ('Leetcode', 'Leetcode'),
        ('Cmd', 'Cmd'),
        ('jquery', 'jquery'),
        ('个人信息', '个人信息'),
        ('Celery', 'Celery'),
        ('Pyecharts', 'Pyecharts'),
        ('javaScripts', 'javaScripts'),
        ('Restful Api', 'Restful Api'),
        ('Flask', 'Flask'),
        ('深度学习', '深度学习'),
        ('Redis', 'Redis'),
        ('Mongodb', 'Mongodb'),
        ('Spring', 'Spring'),
        ('Oracle', 'Oracle'),
        ('Javaweb', 'Javaweb'),
        ('SpringMVC', 'SpringMVC'),
        ('Vue','Vue'),
        ('Mybatis','Mybatis'),
        ('Docker','Docker'),
    )
    status_choices = [  # 文章状态
        ('Draft', 'Draft'),  # 草稿
        ('Published', 'Published'),  # 出版
    ]
    note_author = models.ForeignKey(User, related_name='note_author', on_delete=models.CASCADE,
                                    verbose_name='笔者', help_text='选择自己')
    title = models.CharField(max_length=50, verbose_name='笔记标题', help_text='确保标题和文章内容对应')
    type = models.CharField(max_length=20, choices=note_type, verbose_name='笔记类型', help_text='选择记录的笔记类型')
    publish_date = models.DateField(max_length=30, auto_now=True, verbose_name='发布日期')
    key_word = models.CharField(max_length=100, null=True, verbose_name='关键字', help_text='提取文章主要的关键字')
    slug = models.SlugField(max_length=50, verbose_name='笔记url', help_text='根据它可以通过url找到你的笔记,强烈建议格式为  "你的用户名_title"')
    note_contents = MDTextField(verbose_name='内容')
    praise = models.IntegerField(default=0, verbose_name='点赞量', help_text='会自动记录，请不要修改')
    read_counts = models.IntegerField(default=0, verbose_name='阅读量', help_text='会自动记录，请不要修改')
    shorthand = models.TextField(verbose_name='简介', help_text='大致描述一下你的笔记内容')
    status = models.CharField(max_length=15, choices=status_choices, default='u', verbose_name='文章状态',
                              help_text='您的笔记当前所属状态')

    note_ = models.Manager()

    class Meta:
        ordering = ('-publish_date',)
        # 增加发布权限,普通用户一开始没有任何权限的，需要手动添加权限
        # 用于添加额外条件
        permissions = (
            ('publish_article', '发布文章'),
            ('draft_article', '起草文章'),
        )

    def __str__(self):
        return self.title

    def prefix_url(self):
        """获取url全路径"""
        return '/notes/user_articles_list/' + str(self.slug)

    @property
    def get_user(self):
        return self.note_author.get_username()

    @property
    def get_head_image(self):
        return str(self.note_author.user.get_headImage)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # 添加笔记后发送信号
        super(Note, self).save(force_insert, force_update, using, update_fields)
        send_inform('add_article', self.get_user, self.title, self.slug, head_image=self.get_head_image)

        '''
        _pk = getattr(self, 'pk', None)
        status = getattr(self,'status')
        if _pk and status == 'Published':
            cls = self.__class__
            signal_notes_created = {
                'id':_pk,
                'title':getattr(self,'title'),
                'slug':getattr(self,'slug'),
                'time':getattr(self,'publish_date').strftime('%Y-%m-%d'),
                'author':getattr(self,'note_author').get_username(),
            }
            # signal_notes_created = json.dumps(signal_notes_created,cls=utils.JsonCustomEncoder)
            
            notes_add.send(
                sender=cls,
                signal_notes_created=signal_notes_created,
                created=True,
            )
            
        elif _pk == None:
            notes_log.error('model保存失败，pk尚未生成')
        '''

    # 丰富已有的字段，定义颜色html
    # 函数名为字段名，返回html，反正最后模型都会转为html显示
    def colored_status(self):
        global color_code
        if self.status == 'Published':
            color_code = 'green'
        elif self.status == 'Draft':
            color_code = 'red'
        return format_html(
            '<span style="color:{};font-size:16px;font-weight:bolder;">{}</span>',
            color_code,
            self.status
        )

    # 修改标题
    colored_status.short_description = '文章状态'


class Note_criticism(models.Model):
    """
    笔记评论模型
    一个用户对应多条评论，一篇笔记对应多条评论
    """
    criticism_author = models.ForeignKey(Information, related_name='criticism_author',
                                         verbose_name='笔记评论者', on_delete=models.CASCADE)
    praise_counts = models.IntegerField(default=0, verbose_name='点赞量', help_text='会自动记录，请不要修改')
    tread_counts = models.IntegerField(default=0, verbose_name='差评量', help_text='会自动记录，请不要修改')
    times = models.IntegerField(default=0, verbose_name='该用户评论总次数', help_text='会自动记录，请不要修改')
    dates = models.DateTimeField(auto_now_add=True, verbose_name='评论日期')
    criticism_content = models.TextField(default='请填写评论内容', verbose_name='评论内容')
    note_slug = models.ForeignKey(Note, related_name='note_slug', verbose_name='笔记',
                                  on_delete=models.CASCADE, help_text='请不要修改')

    Note_criticism_ = models.Manager()

    class Meta:
        ordering = ('-dates',)

    def __str__(self):
        return self.criticism_content


class Note_reply(models.Model):
    """
    笔记评论回复模型
    一个评论对应多条回复，一个用户对应多条回复
    """
    note_criticism = models.ForeignKey(Note_criticism, related_name='note_reply', verbose_name='笔记评论',
                                       on_delete=models.CASCADE, default='')
    praise_counts = models.IntegerField(default=0, verbose_name='点赞量', help_text='会自动记录，请不要修改')
    tread_counts = models.IntegerField(default=0, verbose_name='差评量', help_text='会自动记录，请不要修改')
    times = models.IntegerField(default=0, verbose_name='该用户回复当前笔记总次数', help_text='会自动记录，请不要修改')
    dates = models.DateTimeField(auto_now_add=True, verbose_name='评论日期')
    reply_content = models.TextField(default='请填写回复内容', verbose_name='回复内容')
    reply_author = models.ForeignKey(Information, related_name='criticism_reply_author', on_delete=models.CASCADE,
                                     verbose_name='回复者')

    Note_reply_ = models.Manager()

    class Meta:
        ordering = ('-dates',)

    def __str__(self):
        return self.reply_content



