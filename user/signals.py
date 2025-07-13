from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import *
from shipping.models import ShippingAddress

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):

    if not User.objects.all():

        user = User.objects.create_user(
            username='admin',
            password='admin123!',  
            email='324232@studenti.unimore.it',
            first_name='mich',
            last_name='barbi'
        )

        user.save()

        customer = Customer.objects.create(
            user=user
        )

        ShippingAddress.objects.create(
            customer=customer,
            full_name="Mich Barbi",
            address='123 Main St',
            city='Rome',
            province='Rome',
            postal_code='00100',
            country='Italy'
        )