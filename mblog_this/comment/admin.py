from django.contrib import admin
from django.contrib.auth.models import User

from mainsite.models.mainsite_models import Information
from .models.comment_models import Message, Message_reply


# Register your models here.

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('msg_author', 'message_content', 'dates', 'praise_counts', 'tread_counts')
    ordering = ('-praise_counts',)
    list_per_page = 20
    # search_fields = ('msg_author',)
    list_editable = ('message_content',)
    readonly_fields = ('praise_counts', 'tread_counts', 'times')

    def get_queryset(self, request):
        """
        筛选不同用户查询结果
        :param request: HttpRequest对象
        :return:
        """
        all_result = super().get_queryset(request)
        if request.user.is_superuser:
            return all_result
        else:
            return all_result.filter(msg_author=request.user)


@admin.register(Message_reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('reply_author', 'message', 'reply_content', 'dates', 'praise_counts', 'tread_counts')
    ordering = ('-praise_counts',)
    list_per_page = 20
    # search_fields = ('message',)
    list_editable = ('reply_content',)
    readonly_fields = ('praise_counts', 'tread_counts', 'times')

    def get_queryset(self, request):
        all_result = super().get_queryset(request)
        if request.user.is_superuser:
            return all_result
        else:
            return all_result.filter(reply_author=request.user)
