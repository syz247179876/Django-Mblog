from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission, User


class CustomUser(AbstractUser):
    """
    重写auth的表
    """
    register_time = models.DateField(auto_now_add=True, verbose_name='注册时间')
    user_name = models.CharField(max_length=20, verbose_name='用户名')
    user_password = models.CharField(max_length=50, verbose_name='密码')
    motto = models.CharField(max_length=50, verbose_name='格言')
    hobby = models.CharField(max_length=200, default='', verbose_name='爱好')
    head_image = models.ImageField(upload_to='head', verbose_name='头像')
    email = models.EmailField()

    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'auth_user'

    def __repr__(self):
        return self.user_name
