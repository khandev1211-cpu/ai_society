import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_society.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
import chat.routing

application = ProtocolTypeRouter({
    'http': ASGIStaticFilesHandler(get_asgi_application()),
    'websocket': AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns)),
})