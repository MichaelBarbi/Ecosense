from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import *
from shipping.models import ShippingAddress

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    
    for role in STAFF_ROLES:
        StaffRole.objects.get_or_create(name=role)

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

        users_data = [
            {
                "user": {
                    "username": "both@root.com",
                    "password": "haTr6crA!",
                    "email": "both@root.com",
                    "first_name": "both_first",
                    "last_name": "both_last"
                },
                "roles": ["Sales", "Technical"]
            },
            {
                "user": {
                    "username": "sales@root.com",
                    "password": "haTr6crA!",
                    "email": "sales@root.com",
                    "first_name": "sales_first",
                    "last_name": "sales_last"
                },
                "roles": ["Sales"]
            },
            {
                "user": {
                    "username": "tech@root.com",
                    "password": "haTr6crA!",
                    "email": "tech@root.com",
                    "first_name": "tech_first",
                    "last_name": "tech_last"
                },
                "roles": ["Technical"]
            }
        ]

        for data in users_data:
            user_data = data["user"]
            roles_names = data["roles"]

            user, created = User.objects.get_or_create(username=user_data["username"], defaults=user_data)

            if created:
                user.set_password(user_data["password"])
                user.save()

            staff, _ = Staff.objects.get_or_create(user=user)

            # Associate the roles
            for role_name in roles_names:
                try:
                    role = StaffRole.objects.get(name=role_name)
                    staff.roles.add(role)
                except StaffRole.DoesNotExist:
                    pass 