from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Customer
class Customer(models.Model):
    user = models.OneToOneField(User, related_name="customer", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if hasattr(self.user, 'staff'):
            raise ValidationError("A user can't be both Customer and Staff.")
        super().save(*args, **kwargs)

# Staff
class Staff(models.Model):
    user = models.OneToOneField(User, related_name="staff", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if hasattr(self.user, 'customer'):
            raise ValidationError("Un utente non può essere sia Staff che Customer.")
        super().save(*args, **kwargs)
