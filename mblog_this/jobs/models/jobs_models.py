from django.db import models

# Create your models here.
from django.db.models import Manager


class Jobs(models.Model):
    """
    就职网字段
    """
    job_keyword = models.CharField(max_length=30, verbose_name='职位关键词')  # 职位关键词
    city = models.CharField(max_length=40, verbose_name='地区')  # 工作地区
    salary = models.CharField(max_length=30, verbose_name='月薪')  # salary 月薪
    industry = models.CharField(max_length=50, verbose_name='公司名称')  # 公司名称
    technology_keyword = models.CharField(max_length=50, verbose_name='技术关键词')  # 技术关键词
    scale = models.CharField(max_length=100, verbose_name='公司规模')  # 公司规模
    treatment = models.CharField(max_length=50, verbose_name='待遇')  # 待遇
    education = models.CharField(max_length=50, verbose_name='需求门槛')  # 需求门槛
    publish_time = models.CharField(max_length=30, verbose_name='职位发布日期')  # 职位发布日期
    job_ = Manager()

    class meta:
        ordering = ('-job_keyword', 'publish_time')

    def __repr__(self):
        """
        :return:名字
        """
        return self.job_keyword
