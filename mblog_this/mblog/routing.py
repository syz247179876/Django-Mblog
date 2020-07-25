from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from mainsite import routing as inform_routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    # 下面跟着不同协议路由
    'websocket': AuthMiddlewareStack(
        URLRouter(
            # chat_routing.websocket_urlpatterns,
            inform_routing.websocket_urlpatterns,
        )
    ),
})