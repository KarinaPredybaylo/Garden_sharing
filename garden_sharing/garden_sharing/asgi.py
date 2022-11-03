import os
import garden_sharing.routing
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garden_sharing.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    "websocket":AllowedHostsOriginValidator( AuthMiddlewareStack(
        URLRouter(
            garden_sharing.routing.websocket_urlpatterns
        )
    )
    ),
})
