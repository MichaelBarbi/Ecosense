import os
from django.db import models
from django.core.validators import MinValueValidator
from cryptography.fernet import Fernet
from user.models import Customer
from group.models import *


key = os.getenv("encryptKey")
cipher = Fernet(key.encode())

def encrypt_value(value: str) -> str:
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(value: str) -> str:
    return cipher.decrypt(value.encode()).decode()

# Type of a sensor
class SensorType(models.Model):
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=100, blank=True)
    symbol = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Type of sensor"
        verbose_name_plural = "Types of sensors"
        db_table = "sensor_type"

    def __str__(self):
        return self.name


# Sensors to show in catalog
class Sensor(models.Model):

    image = models.ImageField(upload_to='images/sensors', blank=True, null=True, default="images/sensors/na.png")
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)       # Quantity cannot be < 0
    description = models.TextField(max_length=1000, blank=True)
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10 ,default=0.00, validators=[MinValueValidator(0)])
    types = models.ManyToManyField(SensorType, related_name="sensors")

    class Meta:
        ordering = ["name"]
        verbose_name = "Sensor"
        verbose_name_plural = "Sensors"
        db_table = "sensor"
        constraints = [
            models.CheckConstraint(check=models.Q(price__gte=0), name="price_non_negative") # This creates a db costraint
        ]

    def is_in_orders(self):
        from order.models import OrderItem
        return OrderItem.objects.filter(sensor=self).exists()


# Sensor purchased by a customer
class SensorItem(models.Model):

    sensor = models.ForeignKey(Sensor, related_name="sensorItems", on_delete=models.CASCADE)
    registration_code = models.CharField(max_length=200)
    is_registered = models.BooleanField(default=False)
    api_key = models.CharField(max_length=200)
    order = models.ForeignKey("order.Order", related_name="sensorItems", null=True, blank=True, on_delete=models.SET_NULL)
    password = models.CharField(max_length=200)
    label = models.CharField(max_length=70, blank=True, null=True)
    customer = models.ForeignKey(Customer, related_name="sensorItems", on_delete=models.CASCADE ,null=True, blank=True)
    group = models.ForeignKey(Group, related_name="sensorItems", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "SensorItem"
        verbose_name_plural = "SensorItems"
        db_table = "sensor_item"
        constraints = [
            models.UniqueConstraint(fields=["id","sensor"], name="unique_sensoritem_id_sensor")
        ]

    def save(self, *args, **kwargs):
        if not self.pk: 
            self.registration_code = encrypt_value(self.registration_code)
            self.api_key = encrypt_value(self.api_key)
            self.password = encrypt_value(self.password)
        super().save(*args, **kwargs)


    # Custom getter functions to retrieve data decrypted
    def get_api_key(self):
        return decrypt_value(self.api_key)

    def get_password(self):
        return decrypt_value(self.password)
    
    def get_registration_code(self):
        return decrypt_value(self.registration_code)


