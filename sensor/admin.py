from django.contrib import admin
from .models import *

admin.site.register(SensorType)
admin.site.register(Sensor)
admin.site.register(SensorItem)
