from django.urls import path
from . import views
from .models import *

urlpatterns = [
    path("cart/delete", view=views.CartDeleteView.as_view(), name="delete_cart")
]