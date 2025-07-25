import os
from django.db.models.signals import post_save, post_delete, pre_save, post_migrate
from django.dispatch import receiver
from common.signals import update_total
from ecosense import settings
from sensor.models import SensorType
from sensor.utils.token_utils import generate_api_key, generate_unique_password, generate_unique_registration_code
from .models import *

# Pre-save to update the amount field before saving
@receiver(pre_save, sender=OrderItem)
def update_order_item_amount(sender, instance, **kwargs):
    instance.amount = instance.quantity * instance.sensor.price

# Order Item
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total_price(sender, instance, **kwargs):
    update_total(instance, related_name="orderItems", parent_attr="order", total_field="total_price")

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):

    try:

        # Create the sensors before adding orders
        
        if not SensorType.objects.exists():

            types_data = [
                ("Temperature", "Detects heat", "C"),
                ("Pressure", "Measures pressure", "atm"),
                ("Umidity", "Measures umidity", "RH"),
                ("Salinity", "Measures salinity in water", "ppt"),
            ]

            for name, desc, sym in types_data:
                SensorType.objects.create(name=name, description=desc, symbol=sym)

        if not Sensor.objects.exists():

            sensors_data = [
                {
                    "name": "Sensore di umidità RS PRO",
                    "image": "images/sensors/sensoreUmidita.webp",
                    "quantity": 0,
                    "description": "Sensore di umidità RS PRO, interfaccia Analogico, montaggio a innesto",
                    "price": 3.00,
                    "types": [3]
                },
                {
                    "name": "DHT11 - Sensore digitale di umidità e temperatura",
                    "image": "images/sensors/temperatura-umidita.jpg",
                    "quantity": 0,
                    "description": "Rileva la temperatura in un range da 0° C a 50° C e l'umidità in un range da 20-90% RH (± 5% RH), permettendo di costruire un sistema di monitoraggio di temperatura ed umidità altamente affidabile e dai costi contenuti.",
                    "price": 4.90,
                    "types": [1, 3]
                },
                {
                    "name": "Sensore BME680",
                    "image": "images/sensors/Sensore-BME680.jpg",
                    "quantity": 0,
                    "description": "Un sensore digitale 4 in 1. In grado di rilevare diversi parametri ambientali come: la temperatura, l’umidità, la pressione barometrica ed i composti organici volatili (VOC).",
                    "price": 5.99,
                    "types": [1,2,3]
                },
                {
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

                # Build the absolute path of the image
                image_path = os.path.join(settings.MEDIA_ROOT, data["image"])

                # Extract the file name
                image_filename = os.path.basename(image_path)

                # Create the instance but without an image
                data.pop("image")  # I temporarily remove “image” from the date
                sensor = Sensor.objects.create(**data)

                # Open the image file and assign it to sensor.image
                with open(image_path, 'rb') as img_file:
                    sensor.image.name = f"images/sensors/{image_filename}"
                    sensor.save()

                # Assign the types
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


        if not Order.objects.all():

            # Create Credid Card
            CreditCard.objects.create(
                card_number="1111 1111 1111 1111",
                exp_month=1,
                exp_year=2030
            )

            # Create Order
            orders_data = [
                {
                    "customer": 1,
                    "status": OrderStatus.AWAITING_SHIPMENT,
                    "credit_card": 1,
                },
                {
                    "customer": 1,
                    "status": OrderStatus.AWAITING_SHIPMENT,
                    "credit_card": 1,
                },
                {
                    "customer": 1,
                    "status": OrderStatus.AWAITING_SHIPMENT,
                    "credit_card": 1,
                },
                {
                    "customer": 1,
                    "status": OrderStatus.AWAITING_SHIPMENT,
                    "credit_card": 1,
                },
            ]

            for od in orders_data:

                Order.objects.create(
                    customer=Customer.objects.get(pk=od["customer"]),
                    status=od["status"],
                    credit_card=CreditCard.objects.get(pk=od["credit_card"])
                )

            # Create Order items
            order_items_data = [
                {
                    "order": 1,
                    "quantity": 1,
                    "sensor": 1,
                },
                {
                    "order": 2,
                    "quantity": 1,
                    "sensor": 2,
                },
                {
                    "order": 3,
                    "quantity": 1,
                    "sensor": 3,
                },
                {
                    "order": 4,
                    "quantity": 1,
                    "sensor": 4,
                },
            ]

            for oid in order_items_data:

                order = Order.objects.get(pk=oid["order"])
                quantity = oid["quantity"]
                sensor = Sensor.objects.get(pk=oid["sensor"])

                OrderItem.objects.create(
                    order=order,
                    quantity=quantity,
                    sensor=sensor
                )

                # Assign sensor items
                for _ in range(0,quantity):

                    sensorItem = SensorItem.objects.filter(sensor=sensor, order=None).first()

                    if not sensorItem:
                        raise ValueError("SensorItem has not been got")
                    
                    sensorItem.order = order
                    sensorItem.customer = order.customer
                    sensorItem.is_registered = True

                    with open("order/sensorsdata.txt", "a") as f:
                        f.write(sensorItem.get_registration_code() + "\n")
                        f.write(sensorItem.get_password() + "\n")
                        f.write(sensorItem.get_api_key() + "\n")
                        f.write("--------------------------------------" + "\n")

                    sensorItem.save()

    except Exception as e:
        print(str(e))