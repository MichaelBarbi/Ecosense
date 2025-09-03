from django.contrib import admin
from django.urls import path, re_path, include
from . import views
from order import views as orderViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path("404/", views.pageNotFound, name="pageNotFound"),
    path("unauthorized/", views.unauthorized, name="unauthorized"),
    re_path(r'^$|^/$|^home/$', views.home, name="home"),
    
    # User routes
    path('', include('user.urls')),

    # Sensor routes
    path('', include("sensor.urls")),

    # Cart routes
    path("cart/", include("cart.urls")),

    # Order routes
    path('orders/', include("order.urls")),

    # Checkout
    path("checkout/", orderViews.checkoutView, name="checkout"),

    # Group routes
    path('groups/', include("group.urls")),

    # Ticket router
    path('ticket/', include("ticket.urls"))
]
