# -*- coding: utf-8 -*- 
# @Time : 2020/6/17 10:16 
# @Author : 司云中 
# @File : inform_api.py 
# @Software: PyCharm
from mainsite.serializers.inform_serializer import InformSerializer
from rest_framework.fields import empty
from rest_framework.response import Response
from rest_framework.views import APIView
from inform.caches.memcache import MemcacheOperation
from inform.models.inform_models import Inform

import logging

# comment_log = logging.getLogger('comment_')

class InformOperation(APIView):
    """the operation of inform controller"""

    memcache = MemcacheOperation()

    serializer_class = InformSerializer

    @property
    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer(self, instances, context=None, data=empty, many=True):
        serializer_class = self.get_serializer_class
        return serializer_class(instances, many=many)

    def get(self, request):
        IP = request.META.get('REMOTE_ADDR', 'unknown')
        status = self.memcache.save_item(IP, 'login')
        if status:
            informs = Inform.inform_.filter(is_publish=True)
            return Response(self.get_serializer(informs, many=True).data)
        else:
            return Response(None)


