from datetime import datetime,date
import json
from decimal import Decimal
from uuid import UUID

class JsonCustomEncoder(json.JSONEncoder):
    """对时间序列进行编码序列化"""
    # 会判断这个对象是否是可迭代的
    def default(self, obj):
        if isinstance(obj,datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj,date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj,(Decimal,UUID,)):
            return str(obj)
        else:
            return super().default(obj)  # 抛出父类的异常