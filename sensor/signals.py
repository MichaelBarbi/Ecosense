from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import *

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
            quantity=10,
            description="Sensore di umidità RS PRO, interfaccia Analogico, montaggio a innesto",
            price=3.00
        )
        sensor.types.add(3)

