from django.db.models.signals import post_save, post_delete
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import *

from .utils.token_utils import (
    generate_unique_registration_code,
    generate_unique_password,
    generate_api_key,
)

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

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):

    if not SensorType.objects.exists():

        SensorType.objects.create(pk=1, name="Temperature", description="Detects heat", symbol="C")
        SensorType.objects.create(pk=2, name="Pressure", description="Measures pressure", symbol="atm")
        SensorType.objects.create(pk=3, name="Umidity", description="Measures umidity", symbol="%")
        SensorType.objects.create(pk=4, name="Salinity", description="Measures salinity in water", symbol="ppt")

    if not Sensor.objects.exists():
        
        sensor = Sensor.objects.create(
            pk=1,
            name="Sensore di umidità RS PRO",
            image="images/sensors/sensoreUmidita.webp",
            quantity=0,
            description="Sensore di umidità RS PRO, interfaccia Analogico, montaggio a innesto",
            price=3.00
        )
        sensor.types.add(3)

    if not SensorItem.objects.exists():

        SensorItem.objects.create(
            sensor=sensor,
            registration_code=generate_unique_registration_code(),
            is_registered=False,
            api_key=generate_api_key(),
            order=None,
            password=generate_unique_password(),
            label=""
        )

        SensorItem.objects.create(
            sensor=sensor,
            registration_code=generate_unique_registration_code(),
            is_registered=False,
            api_key=generate_api_key(),
            order=None,
            password=generate_unique_password(),
            label=""
        )




