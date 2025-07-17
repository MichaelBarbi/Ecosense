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

        types_data = [
            (1, "Temperature", "Detects heat", "C"),
            (2, "Pressure", "Measures pressure", "atm"),
            (3, "Umidity", "Measures umidity", "RH"),
            (4, "Salinity", "Measures salinity in water", "ppt"),
        ]

        for pk, name, desc, sym in types_data:
            SensorType.objects.create(pk=pk, name=name, description=desc, symbol=sym)

    if not Sensor.objects.exists():

        sensors_data = [
            {
                "pk": 1,
                "name": "Sensore di umidità RS PRO",
                "image": "images/sensors/sensoreUmidita.webp",
                "quantity": 0,
                "description": "Sensore di umidità RS PRO, interfaccia Analogico, montaggio a innesto",
                "price": 3.00,
                "types": [3]
            },
            {
                "pk": 2,
                "name": "DHT11 - Sensore digitale di umidità e temperatura",
                "image": "images/sensors/temperatura-umidita.jpg",
                "quantity": 0,
                "description": "Rileva la temperatura in un range da 0° C a 50° C e l'umidità in un range da 20-90% RH (± 5% RH), permettendo di costruire un sistema di monitoraggio di temperatura ed umidità altamente affidabile e dai costi contenuti.",
                "price": 4.90,
                "types": [1, 3]
            },
            {
                "pk": 3,
                "name": "Sensore BME680",
                "image": "images/sensors/Sensore-BME680.jpg",
                "quantity": 0,
                "description": "Un sensore digitale 4 in 1. In grado di rilevare diversi parametri ambientali come: la temperatura, l’umidità, la pressione barometrica ed i composti organici volatili (VOC).",
                "price": 5.99,
                "types": [1,2,3]
            },
            {
                "pk": 4,
                "name": "Misuratore di salinità HK-47",
                "image": "images/sensors/salinita.jpg",
                "quantity": 0,
                "description": "Misuratore di salinità, tester del sensore di salinità dell'acqua di mare dell'acqua salata Strumento di misurazione della salinità ad alta precisione per la piscina dell'acqua salata",
                "price": 37.21,
                "types": [4]
            }
        ]

        for data in sensors_data:
            types = data.pop("types")
            sensor = Sensor.objects.create(**data)
            sensor.types.add(*types)

        if not SensorItem.objects.exists():

            sensor_items_data = [
                (1, 200),  #Ex. sensor 1 => 200 items
                (2, 100),  
                (3, 40),  
                (4, 50)
            ]

            for sensor_pk, count in sensor_items_data:

                sensor = Sensor.objects.get(pk=sensor_pk)
                
                for _ in range(count):
                    SensorItem.objects.create(
                        sensor=sensor,
                        registration_code=generate_unique_registration_code(),
                        is_registered=False,
                        api_key=generate_api_key(),
                        order=None,
                        password=generate_unique_password(),
                        label=""
                    )





