from django.contrib import admin
from .models import *

admin.site.register(SensorType)

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    readonly_fields = ['quantity']

@admin.register(SensorItem)
class SensorItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'sensor', 'is_registered', 'order']
    readonly_fields = ['api_key', 'is_registered', 'registration_code', 'password']
    list_filter = ['is_registered', 'sensor']

    # Avoid the manual adding operation
    def has_add_permission(self, request):
        return False
    
admin.site.register(SensorData)
