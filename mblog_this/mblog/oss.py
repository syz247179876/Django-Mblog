# -*- coding: utf-8 -*- 
# @Time : 2020/6/12 21:21 
# @Author : 司云中 
# @File : oss.py 
# @Software: PyCharm

import oss2

# 用户账号密码,AccessKey ID和AccessKey Secret
auth = oss2.Auth('自己的oss的AccessKey', '自己的AccessKey Secret')
# 这个是需要用特定的地址，不同地域的服务器地址不同，不要弄错了

endpoint = 'http://oss-cn-shanghai.aliyuncs.com'
# 你的项目名称，类似于不同的项目上传的图片前缀url不同

# 因为我用的是ajax传到后端方法接受的是b字节文件，需要如下配置。 阿里云oss支持更多的方式，下面有链接可以自己根据自己的需求去写
bucket = oss2.Bucket(auth, endpoint, 'uploadhomework')  # 项目名称

# 这个是上传图片后阿里云返回的uri需要拼接下面这个url才可以访问，根据自己情况去写这步
base_image_url = 'https://uploadhomework.oss-cn-shanghai.aliyuncs.com/'
