from django.contrib.auth.models import User
from django.db import models
from django.db.models import Manager

# 添加时间包
# Create your models here.

import datetime


class Information(models.Model):
    """
    用户数据模型
    """
    user = models.OneToOneField(User, verbose_name='已认证用户', on_delete=models.CASCADE, related_name='user')
    motto = models.CharField(max_length=200, default='', verbose_name='格言', help_text='格言不超过200个字')
    hobby = models.CharField(max_length=200, default='', verbose_name='爱好', help_text='爱好不超过200个字')
    # upload_to字段会在media文件夹下创建upload_to文件夹！
    head_image = models.ImageField(upload_to='head', verbose_name='头像', help_text='支持所有正常头像格式')
    information_ = Manager()

    class Meta:
        verbose_name = '用户详情'  # 为模型提供可读名称
        verbose_name_plural = '用户详情'  # 复数形式

    def __str__(self):
        return self.motto

    @property
    def get_headImage(self):
        return self.head_image


class IPs(models.Model):
    """获取客户访问的ip地址"""
    ips = models.CharField(max_length=30, verbose_name='ip地址')
    time = models.DateTimeField(auto_now=True, verbose_name='登录时间')
    ips_author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='ip_author')
    ip_ = models.Manager()

    class Meta:
        ordering = ('-time',)

    def __str__(self):
        return self.ips

    def __repr__(self):
        return self.ips
