from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/groups/(?P<group_id>\d+)/$", consumers.GroupConsumer.as_asgi()),
    re_path(r"ws/sensor_logs/(?P<sensor_id>\d+)/$", consumers.SensorConsumer.as_asgi()),
]
