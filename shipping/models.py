from django.db import models
from user.models import Customer

# Customer shipping address
class ShippingAddress(models.Model):

    customer = models.OneToOneField(Customer, related_name="shippingAddress", on_delete=models.CASCADE, primary_key=True)
    full_name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    province = models.CharField(max_length=50)