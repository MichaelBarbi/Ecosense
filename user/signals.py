from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import *
from shipping.models import ShippingAddress

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):

    if not User.objects.all():

        # Customer data
        customer_data = [
            {
                "username": "mich",
                "password": "1qaz2wsx!QAZ",
                "email": "mich@google.com",
                "first_name": "Michael",
                "last_name": "Barbi",
                "shippingAddress": {
                    "full_name": "Michael Barbi",
                    "address": "via Roma",
                    "city": "Carpi",
                    "province": "Modena",
                    "postal_code": "12345",
                    "country": "Italy"
                }
            },
            {
                "username": "arthurmorgan",
                "password": "1qaz2wsx!QAZ",
                "email": "arthurmorgan@rdr.com",
                "first_name": "Arthur",
                "last_name": "Morgan",
                "shippingAddress": {
                    "full_name": "Arthur Morgan",
                    "address": "Flat Iron Lake Street",
                    "city": "Blackwater",
                    "province": "New Mexico",
                    "postal_code": "10101",
                    "country": "United States"
                }
            },
            {
                "username": "johnmarston",
                "password": "1qaz2wsx!QAZ",
                "email": "johnmarston@rdr.com",
                "first_name": "John",
                "last_name": "Marston",
                "shippingAddress": {
                    "full_name": "John Marston",
                    "address": "Beecher's Hope",
                    "city": "West Elizabeth",
                    "province": "New Mexico",
                    "postal_code": "10102",
                    "country": "United States"
                }
            },
            {
                "username": "dutchvanderlinde",
                "password": "1qaz2wsx!QAZ",
                "email": "dutch@rdr.com",
                "first_name": "Dutch",
                "last_name": "Van der Linde",
                "shippingAddress": {
                    "full_name": "Dutch Van der Linde",
                    "address": "Horseshoe Overlook",
                    "city": "Ambarino",
                    "province": "Colorado",
                    "postal_code": "10103",
                    "country": "Netherlands"
                }
            },
            {
                "username": "sadieadler",
                "password": "1qaz2wsx!QAZ",
                "email": "sadie@rdr.com",
                "first_name": "Sadie",
                "last_name": "Adler",
                "shippingAddress": {
                    "full_name": "Sadie Adler",
                    "address": "Tumbleweed Street",
                    "city": "New Austin",
                    "province": "Texas",
                    "postal_code": "10104",
                    "country": "Scotland"
                }
            },
            {
                "username": "charlessmith",
                "password": "1qaz2wsx!QAZ",
                "email": "charles@rdr.com",
                "first_name": "Charles",
                "last_name": "Smith",
                "shippingAddress": {
                    "full_name": "Charles Smith",
                    "address": "Eagle Flies Road",
                    "city": "Wapiti",
                    "province": "Montana",
                    "postal_code": "10105",
                    "country": "Mexico"
                }
            },
            {
                "username": "micahbell",
                "password": "1qaz2wsx!QAZ",
                "email": "micah@rdr.com",
                "first_name": "Micah",
                "last_name": "Bell",
                "shippingAddress": {
                    "full_name": "Micah Bell",
                    "address": "Mount Hagen Pass",
                    "city": "Ambarino",
                    "province": "Colorado",
                    "postal_code": "10106",
                    "country": "Germany"
                }
            },
            {
                "username": "hoseamatthews",
                "password": "1qaz2wsx!QAZ",
                "email": "hosea@rdr.com",
                "first_name": "Hosea",
                "last_name": "Matthews",
                "shippingAddress": {
                    "full_name": "Hosea Matthews",
                    "address": "Clemens Point",
                    "city": "Lemoyne",
                    "province": "Louisiana",
                    "postal_code": "10107",
                    "country": "Germany"
                }
            },
            {
                "username": "abigailroberts",
                "password": "1qaz2wsx!QAZ",
                "email": "abigail@rdr.com",
                "first_name": "Abigail",
                "last_name": "Roberts",
                "shippingAddress": {
                    "full_name": "Abigail Roberts",
                    "address": "Beecher's Hope",
                    "city": "West Elizabeth",
                    "province": "New Mexico",
                    "postal_code": "10108",
                    "country": "Austria"
                }
            },
            {
                "username": "jackmarston",
                "password": "1qaz2wsx!QAZ",
                "email": "jack@rdr.com",
                "first_name": "Jack",
                "last_name": "Marston",
                "shippingAddress": {
                    "full_name": "Jack Marston",
                    "address": "Beecher's Hope",
                    "city": "West Elizabeth",
                    "province": "New Mexico",
                    "postal_code": "10109",
                    "country": "United States"
                }
            },
            {
                "username": "seanmaguire",
                "password": "1qaz2wsx!QAZ",
                "email": "sean@rdr.com",
                "first_name": "Sean",
                "last_name": "Maguire",
                "shippingAddress": {
                    "full_name": "Sean Maguire",
                    "address": "Emerald Ranch Road",
                    "city": "The Heartlands",
                    "province": "Kansas",
                    "postal_code": "10110",
                    "country": "England"
                }
            },
            {
                "username": "ozzy",
                "password": "1qaz2wsx!QAZ",
                "email": "ozzy@bs.uk",
                "first_name": "Ozzy",
                "last_name": "Osbourne",
                "shippingAddress": {
                    "full_name": "Ozzy Osbourne",
                    "address": "Darkness street",
                    "city": "Birmingham",
                    "province": "Birmingham",
                    "postal_code": "54254",
                    "country": "England"
                }
            },
            {
                "username": "masha123",
                "password": "1qaz2wsx!QAZ",
                "email": "masha@yandex.ru",
                "first_name": "Masha",
                "last_name": "Petrov",
                "shippingAddress": {
                    "full_name": "Masha Petrov",
                    "address": "khaluski molodev",
                    "city": "Moscow",
                    "province": "Moscow",
                    "postal_code": "12450",
                    "country": "Russia"
                }
            }
        ]

        for customer_data in customer_data:
            
            user = User.objects.create_user(
                username=customer_data["username"],
                password=customer_data["password"],  
                email=customer_data["email"],
                first_name=customer_data["first_name"],
                last_name=customer_data["last_name"],
            )        

            user.save()

            customer = Customer.objects.create(
                user=user
            )

            shippingAddressData = customer_data["shippingAddress"]

            ShippingAddress.objects.create(
                customer=customer,
                full_name=shippingAddressData["full_name"],
                address=shippingAddressData["address"],
                city=shippingAddressData["city"],
                province=shippingAddressData["province"],
                postal_code=shippingAddressData["postal_code"],
                country=shippingAddressData["country"]
            )

        staff_data = [
            {
                "user": {
                    "username": "both@root.com",
                    "password": "1qaz2wsx!QAZ",
                    "email": "both@root.com",
                    "first_name": "both_first",
                    "last_name": "both_last"
                },
                "roles": ["Sales", "Technical"]
            },
            {
                "user": {
                    "username": "sales@root.com",
                    "password": "1qaz2wsx!QAZ",
                    "email": "sales@root.com",
                    "first_name": "sales_first",
                    "last_name": "sales_last"
                },
                "roles": ["Sales"]
            },
            {
                "user": {
                    "username": "tech@root.com",
                    "password": "1qaz2wsx!QAZ",
                    "email": "tech@root.com",
                    "first_name": "tech_first",
                    "last_name": "tech_last"
                },
                "roles": ["Technical"]
            }
        ]

        # Create Staff roles
        for name in STAFF_ROLES:
            StaffRole.objects.create(
                name=name
            )

        for data in staff_data:

            user_data = data["user"]
            roles_names = data["roles"]

            user = User.objects.create_user(
                username=user_data["username"],
                password=user_data["password"],  
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
            )   

            staff = Staff.objects.create(
                user=user
            )

            # Associate the roles
            for role_name in roles_names:
                try:
                    role = StaffRole.objects.get(name=role_name)
                    staff.roles.add(role)
                except StaffRole.DoesNotExist as e:
                    print("Error occured while assign roles to staff: " + str(e))
                
            staff.save()
