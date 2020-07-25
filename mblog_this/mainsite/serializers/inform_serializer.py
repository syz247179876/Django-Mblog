# -*- coding: utf-8 -*- 
# @Time : 2020/6/17 11:46 
# @Author : 司云中 
# @File : inform_serializer.py 
# @Software: PyCharm
from inform.models.inform_models import Inform
from rest_framework import serializers


class InformSerializer(serializers.ModelSerializer):
    """the serializer of inform"""

    inform_type = serializers.SerializerMethodField()

    def get_inform_type(self, obj):
        return obj.get_inform_type_display()

    class Meta:
        model = Inform
        fields = '__all__'
