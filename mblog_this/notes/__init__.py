from importlib import import_module

from django.conf import settings
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

DEFAULT_COMMENTS_APP = 'notes'


def get_note_app():
    """if not install this app,an exception will be reported"""
    comments_app = get_note_app_name()
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


def get_note_app_name():
    """
    return name of app in settings.py ,if not exist,the default name of app will be back
    """
    return getattr(settings, 'COMMENTS_APP', DEFAULT_COMMENTS_APP)


def get_model():
    """
    return model of this app
    """
    # Using reflection mechanism to judge whether exist "get_model"
    if get_note_app_name() != DEFAULT_COMMENTS_APP and hasattr(get_note_app(), "get_model"):
        return get_note_app().get_model()
    else:
        from notes.models.notes_models import Note_criticism, Note, Note_reply
        return Note_criticism, Note_reply, Note
