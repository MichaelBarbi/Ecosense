from django.db import models
from django.contrib.auth.models import User

# Customer
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

# Staff
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
