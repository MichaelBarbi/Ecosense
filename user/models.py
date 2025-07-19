from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save
from django.dispatch import receiver

# Customer
class Customer(models.Model):
    user = models.OneToOneField(User, related_name="customer", on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if hasattr(self.user, 'staff'):
            raise ValidationError("A user can't be both Customer and Staff.")
        super().save(*args, **kwargs)


# Permissions as Groups
STAFF_ROLES = ('Technical', 'Sales')

# Staff
class Staff(models.Model):
    user = models.OneToOneField(User, related_name="staff", on_delete=models.CASCADE)
    roles = models.ManyToManyField('StaffRole', blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):

        if hasattr(self.user, 'customer'):
            raise ValidationError("A user can't be both Staff and Customer.")

        # Check if the is_staff attributes it's not set yet
        if not self.user.is_staff:
            self.user.is_staff = True
            self.user.save()
        
        # Set the username equal to the email if not set yet
        if self.user.email and self.user.username != self.user.email:
            self.user.username = self.user.email
            self.user.save()

        super().save(*args, **kwargs)

        # If the staff member doesn't have specificated roles, I assign to him both roles
        if self.roles.count() == 0:
            for role in STAFF_ROLES:

                r, _ = StaffRole.objects.get_or_create(name=role)
                self.roles.add(r)
            self.save()

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()
    
    @property
    def is_sales(self):
        return self.has_role("Sales")
    
    @property
    def is_technical(self):
        return self.has_role("Technical")


# Manage the custom roles
class StaffRole(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# Set email as unique 
@receiver(pre_save, sender=User)
def enforce_unique_email(sender, instance, **kwargs):
    if User.objects.exclude(pk=instance.pk).filter(email=instance.email).exists():
        raise ValidationError("It's alerady exist ad unser with this email")