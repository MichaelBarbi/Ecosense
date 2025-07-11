from django.db import models
from user.models import Customer
from order.models import Order
from django.core.validators import MinValueValidator

# Type of a sensor
class SensorType(models.Model):
    
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=100, blank=True)
    symbol = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Type of sensor"
        verbose_name_plural = "Types of sensors"
        db_table = "sensor_type"


# Sensors to show in catalog
class Sensor(models.Model):

    image = models.TextField(max_length=2000, blank=True)
    quantity = models.PositiveIntegerField(default=0)       # Quantity cannot be < 0
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

# Sensor purchased by a customer
class SensorItem(models.Model):

    sensor = models.ForeignKey(Sensor, related_name="sensorItems", on_delete=models.CASCADE)
    registration_code = models.CharField(max_length=200)
    is_registered = models.BooleanField(default=False)
    api_key = models.CharField(max_length=200)
    order = models.ForeignKey(Order, related_name="sensorItems", null=True, blank=True, on_delete=models.SET_NULL)
    password = models.CharField(max_length=30)
    label = models.CharField(max_length=70, blank=True, null=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "SensorItem"
        verbose_name_plural = "SensorItems"
        db_table = "sensor_item"
        constraints = [
            models.UniqueConstraint(fields=["id","sensor"], name="unique_sensoritem_id_sensor")
        ]

