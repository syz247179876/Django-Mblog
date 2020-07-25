# 绝对导入，把下一个新版本的特性导入到当前版本，例如python3取消了python2.u前缀
from __future__ import absolute_import, unicode_literals

import pymysql

# 用pymysql代替MySQLdb
pymysql.install_as_MySQLdb()
# 暴露接口
from .celery import app as celery_app

__all__ = ['celery_app']
