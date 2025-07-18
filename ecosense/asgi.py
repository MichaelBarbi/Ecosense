import os
from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from sensor import routing

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.routing import Mount

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecosense.settings')

django_asgi_app = get_asgi_application()

main_app = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(routing.websocket_urlpatterns)
    ),
})

# In debug, add support to /static
if settings.DEBUG:
    static_app = Starlette(routes=[
        Mount("/static", app=StaticFiles(directory=settings.STATIC_ROOT), name="static"),
        Mount("/media", app=StaticFiles(directory=settings.MEDIA_ROOT), name="media"),
    ])

    async def application(scope, receive, send):
        if scope["type"] == "http" and (
            scope["path"].startswith("/static") or scope["path"].startswith("/media")
        ):
            await static_app(scope, receive, send)
        else:
            await main_app(scope, receive, send)
else:
    application = main_app
