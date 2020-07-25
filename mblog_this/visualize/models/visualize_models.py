from django.db import models

# Create your models here.
from django.db.models import Manager


class lagou(models.Model):
    """
    创建拉勾网数据表
    """
    city = models.CharField(max_length=20, verbose_name='城市')
    education = models.CharField(max_length=50, verbose_name='学历')
    industry = models.CharField(max_length=50, verbose_name='企业')
    job = models.CharField(max_length=50, verbose_name='职位')
    recruit_name = models.CharField(max_length=50, verbose_name='发布招聘时间')
    salary = models.CharField(max_length=20, verbose_name='月薪')
    scale = models.CharField(max_length=50, verbose_name='企业规模', default='')
    technique_key = models.CharField(max_length=50, verbose_name='技术关键词', default='')
    treatment = models.CharField(max_length=100, verbose_name='待遇', default='')

    lagou_ = Manager()

    def __repr__(self):
        return self.job

    def __str__(self):
        return self.job

