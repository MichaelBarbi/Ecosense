from django.urls import path
from . import views
from .models import *

urlpatterns = [
    path("cart/", view=views.CartPageView.as_view(), name="cart"),
    path("cart/delete-item/<int:item_id>", view=views.cart_delete_item, name="cart_delete_item"),
    path("cart/update-item/<int:item_id>/increase/", views.increase_quantity, name="cart_increase_quantity"),
    path("cart/update-item/<int:item_id>/decrease/", views.decrease_quantity, name="cart_decrease_quantity"),
    path("checkout/", views.checkoutView, name="checkout"),
    path("orders/", views.CustomerOrdersListView.as_view(), name="orders"),
    path("orders/<int:order_id>/", views.CustomerOrderView.as_view(), name="order")
]