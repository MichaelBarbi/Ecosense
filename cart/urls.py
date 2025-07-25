from django.urls import path
from . import views
from .models import *

app_name = "cart"

urlpatterns = [
    path("", view=views.CartPageView.as_view(), name="cart"),
    path("delete-item/<int:item_id>", view=views.cart_delete_item, name="cart_delete_item"),
    path("update-item/<int:item_id>/increase/", views.increase_quantity, name="cart_increase_quantity"),
    path("update-item/<int:item_id>/decrease/", views.decrease_quantity, name="cart_decrease_quantity")
]