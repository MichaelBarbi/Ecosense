from django.urls import path
from . import views

app_name = "groups"

urlpatterns = [
   path('add/', views.addGroupView, name="add_group"),
   path('<int:group_id>/', views.groupView, name="manage"),
   path('<int:group_id>/remove-sensor', views.removeSensorFromGroup, name="remove_sensor_from_group"),
]