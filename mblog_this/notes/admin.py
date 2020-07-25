from django.contrib import admin
from notes.models import notes_models
from django.contrib.auth.decorators import permission_required

import jieba

# Register your models here.
from notes.models.signals import notes_add


@admin.register(notes_models.Note)
class NotesAdmin(admin.ModelAdmin):
    exclude = ('note_author',)

    list_display = (
        'title', 'type', 'key_word', 'praise', 'read_counts', 'colored_status', 'publish_date')
    # 按照type降序排列
    ordering = ('-type',)
    # 绑定actions方法
    actions = ['make_published', 'make_draft', 'confirm_author']
    # 动作按钮在上方
    actions_on_top = True
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 20
    # 设置可以选择的编辑字段
    list_editable = ('type',)
    # 搜索字段
    search_fields = ('type',)
    # 筛选器
    list_filter = ('title', 'type', 'key_word', 'status')  # 过滤器
    # 只读字段
    readonly_fields = ('read_counts', 'praise',)

    # 权限验证装饰器,用户需要拥有article权限,没有权限报403异常
    # @permission_required('Note.publish_article', raise_exception=True)

    def get_slug(self):
        return

    def save_model(self, request, obj, form, change):
        """保存对象后的自动添加作者"""
        obj.note_author = request.user
        # 后面弄懂了save源码，再结合jieba和有道翻译，自动生成slug
        super().save_model(request, obj, form, change)

    def get_signal_details(self, quertset):
        signal_notes_created = {
            'id': getattr(quertset, 'pk'),
            'title': getattr(quertset, 'title'),
            'slug': getattr(quertset, 'slug'),
            'time': getattr(quertset, 'publish_date').strftime('%Y-%m-%d'),
            'author': getattr(quertset, 'note_author').get_username(),
        }
        return signal_notes_created

    def make_published(self, request, querysets):
        """
        修改文章状态为发布的动作
        :param NotesAdmin: 当前模型的model的amidn
        :param request:当前Request对象
        :param querysets:包含用户选择的对象，QuerySet对象
        :return:
        """
        result = querysets.update(status='Published')
        # 返回更新条数
        if result == 1:
            message_shorthand = '1 article was published'
        else:
            message_shorthand = '{number} articles were published'.format(number=result)
        for queryset in querysets:
            get_signal_details = getattr(self, 'get_signal_details')
            # send方法必须是关键字参数，否则报错
            notes_add.send(
                sender=notes_models.Note,
                signal_notes_created=get_signal_details(queryset),
                created=True
            )
        self.message_user(request, 'successfully modified ！ {action_msg}'.format(action_msg=message_shorthand))

    # 对该动作的简短描述
    make_published.short_description = "发布文章"

    # permission_required(perm, login_url=None, raise_exception=False)
    # @permission_required('Note.draft_article', raise_exception=True)
    def make_draft(self, request, querysets):
        """
        修改文章状态为草稿的动作
        :param querysets:
        :param request:
        :return:
        """
        result = querysets.update(status='Draft')
        # 返回更新条数
        if result == 1:
            message_shorthand = '1 article was drafted'
        else:
            message_shorthand = '{number} articles were drafted'.format(number=result)
        self.message_user(request, 'successfully modified ！ {action_msg}'.format(action_msg=message_shorthand))

    make_draft.short_description = '保存草稿'

    def confirm_author(self, request, querysets):
        """
        一键归档
        :param request:
        :param querysets:
        :return:
        """
        if request.user.is_superuser:
            result = querysets.update(note_author=request.user)
            if result == 1:
                message_shorthand = '1 article belongs to {author}'.format(author=request.user.username)
            else:
                message_shorthand = '{number} article belong to {author}'.format(number=result,
                                                                                 author=request.user.username)
            self.message_user(request, 'successfully modified ！ {action_msg}'.format(action_msg=message_shorthand))

    confirm_author.short_description = '归档'

    def get_queryset(self, request):
        all_result = super().get_queryset(request)
        if request.user.is_superuser:
            return all_result
        else:
            return all_result.filter(note_author=request.user)


@admin.register(notes_models.Note_criticism)
class Notes_criticismAdmin(admin.ModelAdmin):
    list_display = ('criticism_author', 'dates', 'criticism_content', 'note_slug')
    ordering = ('dates',)
    # 设置可以选择的编辑字段
    list_editable = ('criticism_content',)
    list_per_page = 10
    # 筛选器
    list_filter = ('note_slug', 'dates')  # 过滤器
    # 只读字段
    readonly_fields = ('note_slug', 'dates', 'criticism_author', 'praise_counts', 'tread_counts', 'times')

    def has_add_permission(self, request, obj=None):
        # obj为当前模型对象
        if request.user.is_superuser:
            return True
        else:
            return False


@admin.register(notes_models.Note_reply)
class Notes_replyAdmin(admin.ModelAdmin):
    list_display = ('reply_author', 'note_criticism', 'dates', 'reply_content')
    ordering = ('dates',)
    list_editable = ('reply_content',)
    list_per_page = 10
    # 筛选器
    list_filter = ('note_criticism', 'dates')  # 过滤器
    # 只读字段
    readonly_fields = ('note_criticism', 'dates', 'reply_author', 'tread_counts', 'praise_counts', 'times')

    def has_add_permission(self, request, obj=None):
        # obj为当前模型对象
        if request.user.is_superuser:
            return True
        else:
            return False


admin.site.site_header = '云博后台管理系统'
admin.site.site_title = '云博后台管理系统'
# admin.site.register(notes_models.Note, NotesAdmin)
# admin.site.register(notes_models.Note_criticism, Notes_criticismAdmin)
# admin.site.register(notes_models.Note_reply, Notes_replyAdmin)
