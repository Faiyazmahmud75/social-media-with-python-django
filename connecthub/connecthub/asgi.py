import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connecthub.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing
import chats.routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns  + chats.routing.websocket_urlpatterns
        )
    ),
})
