
class NotRedis(Exception):
    """
    抛出异常当没有Redis实例加载失败的时候

    """
    pass

class NotCreated(Exception):
    """当Created字段设置为True时，抛出异常，应该在Created为True是发送评论信号"""
    pass