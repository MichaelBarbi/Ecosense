from django.test import TestCase, Client
from django.urls import reverse
from payment.forms import CreditCardForm
from sensor.forms import SensorItemAddForm
from sensor.models import SensorItem, SensorType
from .models import Customer, Order
from shipping.models import ShippingAddress
from payment.models import CreditCard
from django.contrib.auth.models import User
from cart.models import *
from datetime import date

class CheckoutViewTest(TestCase):

    def setUp(self):

        self.client = Client()
        
        # Create a test customer
        test_user = User.objects.create_user(
            username="test",
            password="1qaz2wsx!QAZ",  
            email="test@test.com",
            first_name="test_name",
            last_name="test_surname",
        ) 

        self.customer = Customer.objects.create(user=test_user)
        self.client.login(username="test", password="1qaz2wsx!QAZ")

        #------------------------------------------------------------------------------------

        # Create a shippingAddress
        self.shipping_address = ShippingAddress.objects.create(
            customer=self.customer,
            full_name="test test",
            address="Via Roma 1",
            city="Rome",
            postal_code="00100",
            province="Rome",
            country="Italy"
        )

        #------------------------------------------------------------------------------------

        # Create sensors

        sensors_data = [
            {
                "name": "Sensor1",
                "description": "Sensor1 description",
                "price": 10.00,
            },
            {
                "name": "Sensor2",
                "description": "Sensor2 description",
                "price": 5.00,
            },
        ]

        self.sensors = []

        sensorType, created = SensorType.objects.get_or_create(name="Temperature", defaults={"symbol": "C"})

        for sensor in sensors_data:

            newSensor = Sensor.objects.create(
                name=sensor["name"],
                description=sensor["description"],
                price=sensor["price"]
            )

            newSensor.types.add(sensorType)

            self.sensors.append(newSensor)

        # Create 3 SensorItem

        SensorItem.objects.create(
            sensor=self.sensors[0],
            registration_code="1111",
            is_registered=False,
            api_key="1111",
            order=None,
            password="1111",
            label="",
            customer=None,
            group=None
        )

        SensorItem.objects.create(
            sensor=self.sensors[1],
            registration_code="2222",
            is_registered=False,
            api_key="2222",
            order=None,
            password="2222",
            label="",
            customer=None,
            group=None
        )

        SensorItem.objects.create(
            sensor=self.sensors[1],
            registration_code="2222",
            is_registered=False,
            api_key="2222",
            order=None,
            password="2222",
            label="",
            customer=None,
            group=None
        )

        #------------------------------------------------------------------------------------

        # Create a cart
        self.cart = Cart.objects.create(
            customer=self.customer,
            total_price=20.00
        )

        #------------------------------------------------------------------------------------

        # Create cartitems
        
        CartItem.objects.create(
            cart=self.cart,
            quantity=1,
            sensor=self.sensors[0],
            amount=10.00
        )

        CartItem.objects.create(
            cart=self.cart,
            quantity=2,
            sensor=self.sensors[1],
            amount=10.00
        )

        #------------------------------------------------------------------------------------

        # CreditCard
        self.valid_card_data = {
            "card_number": "1234 5678 9012 3456",
            "exp_month": 12,
            "exp_year": 2027,
            "cvc": "123"
        }

    # Cart missing
    def test_checkout_fails_if_cart_missing(self):

        self.cart.delete()
        self.customer.save()

        response = self.client.post(reverse("checkout"), data=self.valid_card_data, follow=True)

        # Verify if the response has been redirect to cart page again after the failure
        self.assertRedirects(response, reverse("cart:cart"))

        # Obtain a list with all django messages
        messages = list(response.wsgi_request._messages)

        # Verify that the error message that I raise is actually present
        self.assertIn("Customer has no cart", str(messages[0]))

    # Verify every data combination for CreditCardForm
    def test_credit_card_form_combinations(self):

        year = date.today().year
        month = date.today().month
        exp_year = year + 3

        test_cases = [
            {"card_number": "", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": False}, # card_number is empty
            {"card_number": None, "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": False}, # card_number is None
            {"card_number": "1111 2222 3333 444", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": False}, # card_number is too short
            {"card_number": "1111 2222 3333 44444", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": False}, # card_number is too long
            {"card_number": "1111 2222 3333 44f4", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": False}, # card_number doens't contain only digits
            {"card_number": "1111 2222 3333 4444", "exp_month": 0, "exp_year": exp_year, "cvc": 123, "valid": False}, # month is < 1
            {"card_number": "1111 2222 3333 4444", "exp_month": 13, "exp_year": exp_year, "cvc": 123, "valid": False}, # month is > 12
            {"card_number": "1111 2222 3333 4444", "exp_month": "f1", "exp_year": exp_year, "cvc": 123, "valid": False}, # month is not a number
            {"card_number": "1111 2222 3333 4444", "exp_month": 12, "exp_year": (year-1), "cvc": 123, "valid": False}, # year contains the previus year
            {"card_number": "1111 2222 3333 4444", "exp_month": (month-1), "exp_year": year, "cvc": 123, "valid": False}, # Same year but previous month
            {"card_number": "1111 2222 3333 4444", "exp_month": 12, "exp_year": "2030f", "cvc": 123, "valid": False}, # year is not a number
            {"card_number": "1111 2222 3333 4444", "exp_month": 12, "exp_year": exp_year, "cvc": 12, "valid": False}, # cvc is too short
            {"card_number": "1111 2222 3333 4444", "exp_month": 12, "exp_year": exp_year, "cvc": 12345, "valid": False}, # cvc is too long
            {"card_number": "1111 2222 3333 4444", "exp_month": 12, "exp_year": exp_year, "cvc": "12f", "valid": False}, # cvc is not a number

            {"card_number": "1111 2222 3333 4444", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": True},   # General case

            {"card_number": " 1111 2222 3333 4444", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": True},
            {"card_number": "-1111 2222 3333 4444", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": True},
            {"card_number": "1111 2222 3333 4444 ", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": True},
            {"card_number": "1111 2222 3333 4444-", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": True},
            {"card_number": "1111222233334444", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": True},
            {"card_number": "1111-2222-3333-4444", "exp_month": 12, "exp_year": exp_year, "cvc": 123, "valid": True},

            {"card_number": "1111 2222 3333 4444", "exp_month": "12", "exp_year": exp_year, "cvc": 123, "valid": True},

            {"card_number": "1111 2222 3333 4444", "exp_month": month, "exp_year": year, "cvc": 123, "valid": True},
            {"card_number": "1111 2222 3333 4444", "exp_month": 12, "exp_year": str(exp_year), "cvc": 123, "valid": True},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                form = CreditCardForm(data=case)
                self.assertEqual(form.is_valid(), case["valid"])

    # Verify that the order has been succesfully created
    def test_valid_checkout_creates_order_and_redirects(self):

        response = self.client.post(reverse("checkout"), data=self.valid_card_data)

        # Verify that the order has been created
        ordersCount = Order.objects.filter(customer=self.customer).count()
        self.assertEqual(ordersCount, 1)

        order = Order.objects.get(customer=self.customer)

        self.assertEqual(order.customer, self.customer)
        self.assertEqual(float(order.total_price), 20.00)

        # Verify that tha card has been saved
        self.assertEqual(CreditCard.objects.filter(orders=order).count(), 1)

        self.assertRedirects(response, reverse("home"))

    # Verify that the order matches the total price of the cart and his orderItems are equal to cartItems. 
    def test_orderitems_match_cartitems(self):

        response = self.client.post(reverse("checkout"), data=self.valid_card_data)

        order = Order.objects.get(customer=self.customer)
        order_items = order.orderItems.all()

        self.assertEqual(order.total_price, self.cart.total_price)

        # Create a cart
        self.cart = Cart.objects.create(
            customer=self.customer,
            total_price=20.00
        )

        #------------------------------------------------------------------------------------

        # Create cartitems
        
        CartItem.objects.create(
            cart=self.cart,
            quantity=1,
            sensor=self.sensors[0],
            amount=10.00
        )

        CartItem.objects.create(
            cart=self.cart,
            quantity=2,
            sensor=self.sensors[1],
            amount=10.00
        )

        self.assertEqual(len(order_items), len(self.cart.cartItems.all()))

        cart_items = list(self.cart.cartItems.all())

        for i in range(0, len(order_items)):
            self.assertEqual(order_items[i].sensor, cart_items[i].sensor)
            self.assertEqual(order_items[i].quantity, cart_items[i].quantity)
            self.assertEqual(order_items[i].amount, cart_items[i].amount)

    # Verify that after the creation of the order, a number of sensorItems requested by OrderItems have been selected => SensorItem order attribute = this order
    def test_sensor_items_associated_to_order(self):

        self.client.post(reverse("checkout"), data=self.valid_card_data)
        order = Order.objects.get(customer=self.customer)

        count = SensorItem.objects.filter(order=order).count()

        self.assertEqual(count, 3)

    """
    Verify that a new sensor item is only added if it passes certain safety checks.

    - Registration Code
        - Must be unique
        - Must have the format: XXXXX-XXXXX-XXXXX
    - Password
        - Must be validated by django password validator
    - Api Key
        - Must be unique
        - Must be validated by django password validator
    - Sensor
        - Must be an existing sensor
    """ 
    def test_adding_a_sensor_item(self):

        #Set up data

        newSensor = Sensor.objects.create(
            name="Sensor Test",
            description="Sensor Test Description",
            price=3.99
        )
        
        SensorItem.objects.create(
            sensor=newSensor,
            registration_code="AAAAA-AAAAA-AAAAA",
            is_registered=False,
            api_key="h6Ar5rc!tgyvftdeydedd",
            order=None,
            password="u67v6Axeyvu!vrt3xety3",
            label="",
            customer=None,
            group=None
        )

        # Django password validators
        # - Password can't have a length < 8
        # - Password cannot be too common
        # - Password can't be all numbers. It needs at least 1 not numeric character 
        
        test_cases = [
            # The registration code has already been used
            {"registration_code": "AAAAA-AAAAA-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "aaaaa-aaaaa-aaaaa", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The length of the registration code is too short
            {"registration_code": "AAAA-AAAAA-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA-AAAA-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA-AAAAA-AAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The length of the registration code is too long
            {"registration_code": "1AAAAA-AAAAA-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA-1AAAAA-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA-AAAAA-1AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA1-AAAAA-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA-AAAAA1-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA-AAAAA-AAAAA1", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The registration code can't accept not alphanumerical characters
            {"registration_code": "AA!!A-12#44-A$&%S", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "BBBBA-BBBBA-BSBB!", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The position of the symbol '-' for reregistration code is invalid
            {"registration_code": "AAAAAAAAAAAAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAAAAAAA-AAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "AAAAA-AAAAAAAAAA", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "-AAAAA-AAAAA-AAAAA-", "password": "743Ar674v6ddd56c!", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The password length is < 8 characters
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "1qaz", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "1qaz!d4", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The password can't be too common
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "football", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "asdfghjkl", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The password can't be only numerical
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "123456789", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "783465643856435634343443434", "api_key": "743Ar674v6ddd56c!", "sensor": newSensor.id, "valid": False},

            # The api key has already been used
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hh2ggy3t4fvrtgAFAF", "api_key": "h6Ar5rc!tgyvftdeydedd", "sensor": newSensor.id, "valid": False},

            # The api key length is < 8 characters
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "1g2r", "sensor": newSensor.id, "valid": False},
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "gde!ft2", "sensor": newSensor.id, "valid": False},

            # The api key can't be too common
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "football", "sensor": newSensor.id, "valid": False},
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "asdfghjkl", "sensor": newSensor.id, "valid": False},

            # The api key can't be only numerical
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "123456789", "sensor": newSensor.id, "valid": False},
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "783465643856435634343443434", "sensor": newSensor.id, "valid": False},

            # The sensor ID passed doesn't exist
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "uy6v54cGYFT!yguytefty22", "sensor": 9999, "valid": False},

            # Positive cases
            {"registration_code": "1AAAA-AAAAA-AAAA1", "password": "hude6tf54e4!hgygty", "api_key": "uy6v54cGYFT!yguytefty22", "sensor": newSensor.id, "valid": True},
            {"registration_code": "BAAAA-AAAAA-AAAAA", "password": "hude226tf54e4!hgygty", "api_key": "uy622v54cGYFT!yguytefty22", "sensor": newSensor.id, "valid": True},
            {"registration_code": "12345-12345-12345", "password": "hude6tf5433e4!hgygty", "api_key": "uy6v5324cGYFT!yguytefty22", "sensor": newSensor.id, "valid": True},
            {"registration_code": "swsww-12345-deded", "password": "hude6tf54e14!hgygty", "api_key": "uy6v54cGYF1T!yguytefty22", "sensor": newSensor.id, "valid": True},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                form = SensorItemAddForm(data=case)                
                self.assertEqual(form.is_valid(), case["valid"])
