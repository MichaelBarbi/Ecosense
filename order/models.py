from django.core.validators import MinValueValidator
from django.db import models
from user.models import Customer
from sensor.models import Sensor
from payment.models import CreditCard

class Cart(models.Model):

    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="cart")
    total_price = models.DecimalField(decimal_places=2, max_digits=10 ,default=0.00, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["id"]
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        db_table = "cart"
        constraints = [
            models.CheckConstraint(check=models.Q(total_price__gte=0), name="cart_totalPrice_non_negative")
        ]

class CartItem(models.Model):

    cart = models.ForeignKey(Cart, related_name="cartItems", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    sensor = models.ForeignKey(Sensor, related_name="cartItems", on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10 ,default=0.00, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["id"]
        verbose_name = "Cart item"
        verbose_name_plural = "Cart items"
        db_table = "cart_item"
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0), name="cartItem_amount_non_negative")
        ]

class OrderStatus(models.IntegerChoices):
    PENDING = 1, "Pending"
    AWAITING_PAYMENT = 2, "Awaiting Payment"
    AWAITING_SHIPMENT = 3, "Awaiting Shipment"
    COMPLETED = 4, "Completed"
    CANCELLED = 5, "Cancelled"

class Order(models.Model):

    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(decimal_places=2, max_digits=10 ,default=0.00, validators=[MinValueValidator(0)])
    status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING)
    credit_cart = models.ForeignKey(CreditCard, null=True, related_name="orders", on_delete=models.SET_NULL)

    class Meta:
        ordering = ["id"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        db_table = "order"
        constraints = [
            models.CheckConstraint(check=models.Q(total_price__gte=0), name="order_totalPrice_non_negative")
        ]

class OrderItem(models.Model):

    order = models.ForeignKey(Order, related_name="orderItems", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    sensor = models.ForeignKey(Sensor, related_name="orderItems", on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10 ,default=0.00, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ["id"]
        verbose_name = "Order item"
        verbose_name_plural = "Order items"
        db_table = "order_item"
        constraints = [
            models.CheckConstraint(check=models.Q(amount__gte=0), name="orderItem_amount_non_negative")
        ]