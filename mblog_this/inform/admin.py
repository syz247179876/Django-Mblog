from django.contrib import admin

# Register your models here.
from inform.models.inform_models import Inform


@admin.register(Inform)
class InformAdmin(admin.ModelAdmin):
    list_display = ('inform_title', 'inform_type', 'inform_time', 'image', 'is_publish')
    list_editable = ('inform_type',)
    actions = ('deliver_inform', 'cancel_inform')

    def has_add_permission(self, request):
        return True if request.user.is_superuser else False

    def has_delete_permission(self, request, obj=None):
        return True if request.user.is_superuser else False

    def has_change_permission(self, request, obj=None):
        return True if request.user.is_superuser else False

    def has_view_permission(self, request, obj=None):
        return True

    def get_actions(self, request):
        """根据不同用户限制权限"""
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            for action in self.actions:
                actions.pop(action)
        return actions

    def deliver_inform(self, request, querysets):
        """发布通知"""
        result = querysets.update(is_publish=True)
        # 返回更新条数
        if result == 1:
            message_shorthand = '1 inform has been cancelled sending'
        else:
            message_shorthand = '{number} informs were published'.format(number=result)
        self.message_user(request, 'successfully modified ！ {action_msg}'.format(action_msg=message_shorthand))

    deliver_inform.short_description = '增加通知'

    def cancel_inform(self, request, querysets):
        """取消发布通知"""
        result = querysets.update(is_publish=False)
        if result == 1:
            message_shorthand = '1 inform has been cancelled sending'
        else:
            message_shorthand = '{number} informs were cancel sending'.format(number=result)
        self.message_user(request, 'successfully modified ！ {action_msg}'.format(action_msg=message_shorthand))

    cancel_inform.short_description = '撤销通知'