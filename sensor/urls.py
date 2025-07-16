from django.urls import path
from . import views
from .models import *

urlpatterns = [
    path("catalog/", views.catalogListView.as_view(), name="catalog"),
    path("catalog/add-to-cart", views.add_to_cart, name="add_to_cart"),
    path("sensors/", views.CustomerRegisteredSensorsListView.as_view(), name="registered_sensors"),
    path("sensors/register", views.registerSensorView, name="register_sensor"),
    path("sensors/<int:pk>/edit/", views.sensorLabelUpdateView, name="edit-sensor"),
    path("sensors/add-group", views.addGroupToSensor, name="add_group_to_sensor"),
    path("sensors/listening", views.receive_sensor_data, name="sensor_listening")
]
