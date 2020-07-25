from django.contrib import admin
from .models.mainsite_models import Information, IPs
from mdeditor.widgets import MDEditorWidget


# Register your models here.

@admin.register(Information)
class InformationAdmin(admin.ModelAdmin):
    list_display = ('user', 'motto', 'hobby', 'head_image')
    list_editable = ('motto', 'hobby', 'head_image')
    readonly_fields = ('user',)

    def has_add_permission(self, request):
        """
        Return True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        """
        Return True if the given request has permission to add an object.
        Can be overridden by the user in subclasses.
        """
        if request.user.is_superuser:
            return True
        else:
            return False

    def get_queryset(self, request):
        """
        筛选数据
        :param request:
        :return:
        """
        all_result = super().get_queryset(request)
        if request.user.is_superuser:
            return all_result
        else:
            return all_result.filter(user=request.user)

    def get_actions(self, request):
        # 在actions中去掉‘删除’操作
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'can delete information' in actions:
                del actions['can delete information']
            if 'can add information' in actions:
                del actions['can add information']
        return actions

    '''
    def get_readonly_fields(self, request, obj=None):
        """
        控制用户只读的字段
        :param request: HttpRequest对象
        :param obj:模型对象
        :return:
        """
        self.readonly_fields = ['user', 'motto', 'hobby','head_image']
        return self.readonly_fields
    '''


@admin.register(IPs)
class IpAdmin(admin.ModelAdmin):
    list_display = ('ips', 'ips_author', 'time')
    ordering = ('-time',)
    list_per_page = 50
    readonly_fields = ('ips', 'ips_author', 'time')

    def get_queryset(self, request):
        all_result = super().get_queryset(request)
        if request.user.is_superuser:
            return all_result
        else:
            return all_result.filter(ips_author=request.user)

    def has_change_permission(self, request, obj=None):
        """
        Return True if the given request has permission to change the given
        Django model instance, the default implementation doesn't examine the
        `obj` parameter.

        Can be overridden by the user in subclasses. In such case it should
        return True if the given request has permission to change the `obj`
        model instance. If `obj` is None, this should return True if the given
        request has permission to change *any* object of the given type.
        """
        return True if request.user.is_superuser else False

    def has_add_permission(self, request, obj=None):
        # obj为当前模型对象
        return True if request.user.is_superuser else False

    def has_delete_permission(self, request, obj=None):
        # 判断是否为超级用户
        return True if request.user.is_superuser else False
