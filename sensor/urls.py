from django.urls import path
from . import views
from .models import *

urlpatterns = [
    path("catalog/", views.catalogListView.as_view(), name="catalog")
]
