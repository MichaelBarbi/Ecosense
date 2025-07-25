from django.urls import path
from . import views
from .models import *

app_name = "order"

urlpatterns = [
    path("/", views.OrdersListView.as_view(), name="orders"),
    path("checkout/", views.checkoutView, name="checkout"),
    path("<int:order_id>/", views.CustomerOrderView.as_view(), name="order"),
    path("<int:pk>/update-status/", views.orderStatusUpdate, name="order_update_status")
]