from django.urls import path, re_path
from mainsite import consumers

websocket_urlpatterns = [
    re_path(r'inform/',consumers.InformConsumer),
]