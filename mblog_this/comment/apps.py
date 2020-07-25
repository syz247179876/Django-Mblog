from django.apps import AppConfig


class CommentConfig(AppConfig):
    name = 'comment'

    def ready(self):
        import comment.moderation

