from django.contrib import admin
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^$|^/$|^home/$', views.home, name="home"),
    
    # User routes
    path('', include('user.urls')),

    # Sensor routes
    path('', include("sensor.urls")),

    # Order and Cart routes
    path('', include("order.urls")),

    # Group routes
    path('groups/', include("group.urls"))
]
