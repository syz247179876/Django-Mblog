from django.contrib import admin
from xadmins.models.xadmin_models import CustomUser
# Register your models here.
class UserInfoAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'email')


admin.site.register(CustomUser, UserInfoAdmin)
