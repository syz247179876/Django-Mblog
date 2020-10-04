import logging

import pandas as pd
import pymysql
import os
import django

# 获取当前路径下的setting文件
# 设置环境变量
# celery是一个问题!!!
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mblog.settings')
# django.setup()
# os.path.dirname()返回上一级目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s-%(name)s-%(levelname)s-%(message)s')

print(BASE_DIR)
class mysql:
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.PORT = 3306
        self.USERNAME = 'root'
        self.PASSWORD = '123456'
        self.DB_NAME = 'syz_user'
        self.CHARSET = 'utf8'

    def get_connect(self):
        connect = pymysql.Connect(
            host=self.HOST,
            port=self.PORT,
            user=self.USERNAME,
            password=self.PASSWORD,
            db=self.DB_NAME,
            charset=self.CHARSET
        )
        cursor = connect.cursor()
        return connect, cursor

    @staticmethod
    def get_csv():
        lagous = pd.read_csv(os.path.join(BASE_DIR, 'static/file/lagou_new.csv').replace('\\', '/'))
        lagous = lagous.where(pd.notnull(lagous), '')
        return lagous

    def save_lagou(self):
        lagous = self.get_csv()
        connect, cursor = self.get_connect()
        queryserlissts = [(data[0], data[1], data[2], data[3], data[4], data[5], data[6],
                           data[7], data[8]) for data in lagous.values]

        sql = 'insert into visualize_lagou(city,education,industry,job,recruit_name,salary,scale,' \
              'technique_key,treatment) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        cursor.executemany(sql, queryserlissts)

        # cursor.execute(sql, queryserlissts[3])
        connect.commit()
        cursor.close()
        connect.close()



