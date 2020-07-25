from django.db import models
from django.db.models import Manager
from django.utils.html import format_html

from django.utils.translation import ugettext as _


# Create your models here.


class Inform(models.Model):
    """the inform table"""

    inform_time = models.DateField(
        verbose_name=_('通知发布日期'),
        auto_now_add=True
    )
    inform_content = models.TextField(
        verbose_name=_('通知内容'),
    )
    inform_title = models.CharField(
        verbose_name=_('通知标题'),
        max_length=50,
        help_text=_('不多于50个字')
    )
    inform_type_choices = (
        ('1', '网站最新修改通知'),
        ('2', '广告通知'),
        ('3', '网站维护通知'),
    )
    inform_type = models.CharField(
        verbose_name=_('通知类型'),
        choices=inform_type_choices,
        max_length=1
    )
    is_publish = models.BooleanField(
        verbose_name=_('是否已发布'),
        default=False,
    )
    inform_image = models.ImageField(
        verbose_name=_('通知图片'),
        upload_to='inform_images',
        blank=True,
        null=True
    )

    def image(self):
        if not self.inform_image:
            return '无图片'
        else:
            return format_html("<img src='{}' style='width:100px;height:100px;'>",
                               self.inform_image.url,
                               )

    inform_ = Manager()

    def __str__(self):
        return self.inform_title

    class Meta:
        ordering = ('-inform_time',)
        verbose_name = '网站通知'         # 为模型提供可读名称
        verbose_name_plural = '网站通知'  # 复数形式
