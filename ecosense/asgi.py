import os
from django.conf import settings
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from sensor import routing

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.routing import Mount

# Set the default Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecosense.settings')

# Get the default ASGI application for Django (handles regular HTTP requests)
django_asgi_app = get_asgi_application()

# Define the main ASGI app to handle different types of connections (HTTP, WebSocket)
main_app = ProtocolTypeRouter({
    "http": django_asgi_app,  # HTTP requests go to the standard Django app
    "websocket": AuthMiddlewareStack(  # WebSocket requests use auth middleware
        URLRouter(routing.websocket_urlpatterns)  # Then routed via WebSocket URL patterns
    ),
})

# If we're in development mode (DEBUG=True), also serve static and media files
if settings.DEBUG:
    # Create a Starlette app to serve static and media files
    static_app = Starlette(routes=[
        Mount("/static", app=StaticFiles(directory=settings.STATIC_ROOT), name="static"),
        Mount("/media", app=StaticFiles(directory=settings.MEDIA_ROOT), name="media"),
    ])

    # Define the final ASGI application to serve static/media or fall back to main_app
    async def application(scope, receive, send):
        # If the request is for static or media files, handle with static_app
        if scope["type"] == "http" and (
            scope["path"].startswith("/static") or scope["path"].startswith("/media")
        ):
            await static_app(scope, receive, send)
        else:
            # Otherwise, handle with the main app (Django + WebSocket)
            await main_app(scope, receive, send)
else:
    # In production, don't serve static/media here — let NGINX or Apache handle it
    application = main_app
