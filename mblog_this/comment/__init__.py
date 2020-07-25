from importlib import import_module

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

DEFAULT_COMMENTS_APP = 'comment'


def get_comment_app():
    """获取comment的app，如果在INSTALLED_APPS中没有定义，则会报错
     如果没有该app包，则会抛出异常
    """
    comments_app = get_comment_app_name()
    if not apps.is_installed(comments_app):
        raise ImproperlyConfigured(
            "The COMMENTS_APP (%r) must be in INSTALLED_APPS" % comments_app
        )

        # Try to import the package
    try:
        package = import_module(comments_app)
    except ImportError as e:
        raise ImproperlyConfigured(
            "The COMMENTS_APP setting refers to a non-existing package. (%s)" % e
        )
    return package

def get_comment_app_name():
    """
    返回setting文件中的app的name，如果不存在，返回默认`DEFAULT_COMMENTS_APP`
    """
    return getattr(settings, 'COMMENTS_APP', DEFAULT_COMMENTS_APP)

def get_model():
    """
    返回comment的评论model
    """
    # 先判断app名是否正确，然后利用反射机制有没有get_model方法,
    if get_comment_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_comment_app(), "get_model"):
        return get_comment_app().get_model()
    else:
        from comment.models.comment_models import Message, Message_reply
        return Message, Message_reply


