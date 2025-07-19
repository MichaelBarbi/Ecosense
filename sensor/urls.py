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
    path("sensors/listening", views.receive_sensor_data, name="sensor_listening"),
    path("sensor-types/", views.SensorTypeLsitView.as_view(), name="sensor_types"),
    path("sensor-types/add", views.addSensortype, name="sensor_types_add"),
    path("sensor-types/<int:typeId>/edit", views.sensorTypeUpdate, name="sensor_types_update"),
    path("sensor-types/<int:pk>/delete", views.SensorTypeDeleteView.as_view(), name="sensor_types_delete"),
    path("sensors/staff/", views.SensorListView.as_view(), name="sensors"),
    path("sensors/staff/add", views.addSensor, name="sensors_add"),
    path("sensors/staff/<int:pk>/delete", views.SensorDeleteView.as_view(), name="sensors_delete"),
    path("sensors/staff/<int:pk>/update/", views.updateSensor, name="sensors_update"),
    path("sensors/items/", views.SensorItemsListView.as_view(), name="sensor_items"),
    path("sensors/items/add", views.sensorItemAdd, name="sensor_items_add"),
    path("sensors/items/<int:pk>/update", views.sensorItemUpdateView, name="sensor_items_update"),
    path("sensors/items/<int:pk>/delete", views.SensorItemDeleteView.as_view(), name="sensor_items_delete"),
]
