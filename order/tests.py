from django.test import TestCase, Client
from django.urls import reverse
from payment.forms import CreditCardForm
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

        response = self.client.post(reverse("order:checkout"), data=self.valid_card_data, follow=True)

        # Verify if the response has been redirect to checkout page again after the failure
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

        response = self.client.post(reverse("order:checkout"), data=self.valid_card_data)

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

        response = self.client.post(reverse("order:checkout"), data=self.valid_card_data)

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

        self.client.post(reverse("order:checkout"), data=self.valid_card_data)
        order = Order.objects.get(customer=self.customer)

        count = SensorItem.objects.filter(order=order).count()

        self.assertEqual(count, 3)
