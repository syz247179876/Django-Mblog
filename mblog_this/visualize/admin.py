from django.contrib import admin
from .models.visualize_models import lagou


# Register your models here.
@admin.register(lagou)
class lagouAdmin(admin.ModelAdmin):
    list_display = ('city', 'education', 'industry', 'job')

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
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_add_permission(self, request, obj=None):
        # obj为当前模型对象
        if request.user.is_superuser:
            return True
        else:
            return False

    def has_delete_permission(self, request, obj=None):
        # 判断是否为超级用户
        if request.user.is_superuser:
            return True
        else:
            return False

