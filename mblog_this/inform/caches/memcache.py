# -*- coding: utf-8 -*- 
# @Time : 2020/6/17 9:51 
# @Author : 司云中 
# @File : memcache.py 
# @Software: PyCharm
from django.core.cache import caches

from django_redis import get_redis_connection

class MemcacheOperation:
    """the operation of memcache"""

    def __init__(self):
        # self.memcache = caches['memcache']
        self.redis = get_redis_connection('default')
    def save_item(self, key, value):
        """
        save k-v structure
        return True or False whether Key is saved successfully
        """
        try:
            # is_existed = self.memcache.get(key, None)
            is_existed = self.redis.exists(key)
            if is_existed:    
                return False
            else:
                # self.memcache.set(key, value, 3600)
                self.redis.set(key, value, 3600)
                return True
        except Exception as e:
            return False
