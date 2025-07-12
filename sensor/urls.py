from django.urls import path
from . import views
from .models import *

urlpatterns = [
    path("catalog/", views.catalogListView.as_view(), name="catalog"),
    path("catalog/add-to-cart", views.add_to_cart, name="add_to_cart")
]
