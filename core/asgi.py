"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
import django
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter, get_default_application
from channels.security.websocket import AllowedHostsOriginValidator

from chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from mikro.routing import websocket_urlpatterns as mikro_websocket_urlpatterns
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns
from sale.routing import websocket_urlpatterns as sale_websocket_urlpatterns
from account.routing import websocket_urlpatterns as account_websocket_urlpatterns
from user.routing import websocket_urlpatterns as user_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.development')

django_asgi_app = get_asgi_application()



websocket_urlpatterns = chat_websocket_urlpatterns + mikro_websocket_urlpatterns + notifications_websocket_urlpatterns + sale_websocket_urlpatterns + account_websocket_urlpatterns + user_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})
