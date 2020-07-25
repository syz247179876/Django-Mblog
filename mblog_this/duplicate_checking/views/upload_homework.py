import datetime
import logging
import os
import re

from django_redis import get_redis_connection
from mainsite.consumers import inform_handleHomework
from mblog.oss import base_image_url, bucket
from rest_framework.response import Response
from rest_framework.views import APIView

common_log = logging.getLogger('django')
duplicate_log = logging.getLogger('duplicate_')


# '软件工程-1705-17408002125-司云中-JavaEE开发技术-实验2.docx'


# class UploadHomework(APIView):
#     message = {
#         'code': '',
#         'msg': '',
#         'data': ''
#     }
#
#     redis = get_redis_connection('default')
#
#     _name = None
#
#     _project = None
#
#     _article = None
#
#     @property
#     def regex(self):
#         filename_regex = r'([\u4e00-\u9fa5]{4})-(\d{4})-(\d{11}|第[\u4e00-\u9fa5]{1}组)-([\u4e00-\u9fa5]{2,4})-' \
#                          r'([\u4e00-\u9fa5]{2,20}\w*|\w*[\u4e00-\u9fa5]{2,20})-([\u4e00-\u9fa5]{1,10}\w+)'
#         return filename_regex
#
#     def validate_filename(self, filename):
#         pattern = re.compile(self.regex, re.I)
#         result = pattern.findall(filename)
#         try:
#             if len(result):
#                 results = result[0]
#                 self.major = results[0]
#                 self.class_ = results[1]
#                 self.number = results[2]
#                 self.name = results[3]
#                 self.project = results[4]
#                 self.article = results[5]
#                 return True
#             else:
#                 return False
#         except AttributeError as e:
#             return False
#
#     def validate_filetype(self, filename):
#         rename = os.path.splitext(filename)  # 分割文件
#         if rename[1].upper() not in ['.DOC', '.DOCX', '.PPT', '.PPTX', '.XLS', '.XLSX', '.PDF']:
#             return False
#         else:
#             return True
#
#     @staticmethod
#     def get_file_list(filename):
#         return filename.split('-')
#
#     @property
#     def offset(self):
#         """获取日期offset"""
#         today = datetime.datetime.today()
#         today_str = today.strftime('%Y-%m-%d')
#         today_list = today_str.split('-')
#         offsets = ''.join(today_list)
#         return offsets
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, value):
#         self._name = value
#
#     @property
#     def article(self):
#         return self._article
#
#     @article.setter
#     def article(self, value):
#         self._article = value
#
#     @property
#     def project(self):
#         return self._project
#
#     @project.setter
#     def project(self, value):
#         self._project = value
#
#     def validate_every_upload(self, offset, IP, redis, number, article):
#         """限制每天只能上传一次"""
#         KEY = self.get_key(number, IP, article)
#         status2 = True if redis.getbit(IP, offset) else False
#         status = True if redis.getbit(KEY, offset) else False  # 返回值为int类型
#         return status2 or status
#
#     @property
#     def get_base_path(self):
#         # base_path = r'/home/admin/homework/'
#         base_path = r'D:\\syz\\virtualenvs\\MyDjango\\svn_mblog\\'
#         return base_path
#
#     @staticmethod
#     def get_key(number, ip, article):
#         return '%s-%s-%s' % (number, ip, article)
#
#     def post(self, request):
#         """处理上传，redis限流"""
#         file = request.FILES.get('home_work')
#         IP = request.META.get('REMOTE_ADDR', 'unknown')
#         offset = self.offset
#         redis = getattr(self, 'redis')
#         message = getattr(self, 'message')
#         file_name = str(file)
#         isFilename_valid = self.validate_filename(file_name)  # 验证文件名
#         if isFilename_valid and self.validate_every_upload(offset, IP, redis, self.number, self.article):
#             message.update({'code': -2})  # 当天已经提交过一次
#             return Response(message)
#         isFile_type_valid = self.validate_filetype(file_name)  # 验证文件类型
#         if not isFilename_valid or not isFile_type_valid:
#             # 文件名或文件类型有错误
#             message.update({'code': -1})
#             redis.setbit(IP, self.offset, 1)
#             return Response(message)
#         else:
#             try:
#                 dir_name = self.major + self.class_ + self.project + self.article  # 文件名
#                 dir_base_path = self.get_base_path
#                 dir_path = os.path.join(dir_base_path, dir_name)
#                 if not os.path.exists(dir_path):
#                     os.mkdir(dir_path)
#                 # file_list = os.listdir(MEDIA_ROOT)
#                 filename = os.path.join(dir_path, str(file))
#                 # file_serialize = pickle.dumps(file)
#                 # write_down.delay(filename,file_serialize)
#                 with open(filename, 'wb') as homework_F:
#                     # chunks以块的形式将图片大文件写入文件中，如果文件过大，会占用系统内存，导致变慢，因此分块写更好
#                     for i in file.chunks():
#                         homework_F.write(i)
#                 # message.update({'code': 0,'name':self.name,'project':self.project,'article':self.article})
#                 inform_handleHomework('homework', self.article, self.name, self.project) # 回调信号
#                 message.update({'code': 0})
#                 key = self.get_key(self.number, IP, self.article)
#                 redis.setbit(key, self.offset, 1)
#                 return Response(message)
#             except Exception as e:
#                 duplicate_log.error(str(e))
#                 message.update({'code': 500})
#                 return Response(message)


class UploadFile(APIView):
    """上传文件夹或者文件"""
    throttle_scope = 'uploads'

    # '17408002125_司云中_基于Django的购物商场的设计与实现.zip'
    # throttle_classes = [UploadRateThrottle]  # 对请求进行限流

    @property
    def result(self):
        return {
            'code': 0,
            'folder_url': ''
        }

    @property
    def regex(self):
        # filename_regex = r'《软件工程》课程设计-软件工程\d{4}班-\d{11}-[\u4e00-\u9fa5]{2,4}-\w+系统'
        # filename_regex = r'([\u4e00-\u9fa5]{4})-(\d{4})-(\d{11}|第[\u4e00-\u9fa5]{1}组)-([\u4e00-\u9fa5]{2,4})-' \
        # r'([\u4e00-\u9fa5]{2,20}\w*|\w*[\u4e00-\u9fa5]{2,20})-([\u4e00-\u9fa5]{1,10}\w+)'
        filename_regex = r'1705班-\d{11}-[\u4e00-\u9fa5]{2,4}-\w+'
        return filename_regex

    def validate_filename(self, filename):
        pattern = re.compile(self.regex, re.I)
        results = pattern.findall(filename)
        try:
            if len(results):
                return True
            else:
                return False
        except AttributeError as e:
            common_log.info(e)
            return False

    @staticmethod
    def validate_filetype(filename):
        rename = os.path.splitext(filename)  # 分割文件
        if rename[1].upper() not in ['.DOC', '.DOCX', '.PPT', '.PPTX', '.XLS', '.XLSX', '.PDF', '.ZIP', '.RAR']:
            return False
        else:
            return True

    @staticmethod
    def save_file(files, file_folder):
        """
                    上传文件夹
                    :param files 文件夹目录
                    :param file_folder: b字节文件夹
                    :return: 若成功返回图片路径，若不成功返回空
                    """
        # 生成文件编号，如果文件名重复的话在oss中会覆盖之前的文件
        # 生成文件名
        base_img_name = os.path.join(file_folder, str(files)).replace('\\', '/')
        # 生成外网访问的文件路径
        image_name = os.path.join(base_image_url, file_folder, str(files)).replace('\\', '/')
        # 这个是阿里提供的SDK方法 bucket是调用的4.1中配置的变量名
        # 参数分别为文件名，和二进制内容,可以是bytes，str或者类似文件的对象
        res = bucket.put_object(base_img_name, files)
        # 如果上传状态是200 代表成功 返回文件外网访问路径
        # 下面代码根据自己的需求写
        if res.status == 200:
            return image_name
        else:
            return None

    def post(self, request):
        """上传文件夹或者文件"""
        file = request.FILES.get('home_work')
        file_name = str(file)
        is_Filename_valid = self.validate_filename(file_name)
        is_Filetype_valid = self.validate_filetype(file_name)
        if is_Filename_valid and is_Filetype_valid:
            file_url = self.save_file(file, file_folder='微机原理作业')
            result = self.result
            result.update({'file_url': file_url, 'code': 1314})
            return Response(result)
        else:
            return Response(self.result)