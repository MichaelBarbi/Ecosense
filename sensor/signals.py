from django.db.models.signals import post_save, post_delete, post_migrate
from django.dispatch import receiver
from .models import *

def update_sensor_quantity(sensor):

    # Count the SensorItem without order
    count = SensorItem.objects.filter(sensor=sensor, order__isnull=True).count()

    #Update the quantity attribute of the sensor
    sensor.quantity = count
    sensor.save(update_fields=["quantity"])

@receiver(post_save, sender=SensorItem)
def sensoritem_saved(sender, instance, **kwargs):
    update_sensor_quantity(instance.sensor)

@receiver(post_delete, sender=SensorItem)
def sensoritem_deleted(sender, instance, **kwargs):
    update_sensor_quantity(instance.sensor)
    
            