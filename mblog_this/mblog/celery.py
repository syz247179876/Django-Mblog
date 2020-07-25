
from __future__ import absolute_import, unicode_literals

from celery import Celery

from django.conf import settings
from mblog.settings import *

# 获取当前文件名，即为该Django的项目名
# project_name = os.path.split(BASE_DIR)[-1]
project_name = os.path.split(os.path.abspath('.'))[-1]
project_settings = '%s.settings' % project_name

# 设置环境变量(需要在创建celery应用之前设置)，让celery知道django的环境配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', project_settings)

# 实例化Celery，第一个参数 可以把 task 的 name属性 从 __main__.functionname 替换为 tasks.functionname
# 如 add.name == __main__.add  --> tasks.add
app = Celery('tasks', broker=BROKER_URL)

# 使用django的settings文件配置celery,通过实例加载配置模块
app.config_from_object('django.conf:settings')

# Celery加载所有注册的应用
# 指定任务函数的文件夹位置，表示从哪些位置找到任务函数。
app.autodiscover_tasks(settings.INSTALLED_APPS)

