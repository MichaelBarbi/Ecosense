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
    SHIPPED = 4, "Shipped"
    COMPLETED = 5, "Completed"
    CANCELLED = 6, "Cancelled"

class Order(models.Model):

    customer = models.ForeignKey(Customer, related_name="orders", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    total_price = models.DecimalField(decimal_places=2, max_digits=10 ,default=0.00, validators=[MinValueValidator(0)])
    status = models.IntegerField(choices=OrderStatus.choices, default=OrderStatus.PENDING)
    credit_card = models.ForeignKey(CreditCard, null=True, related_name="orders", on_delete=models.SET_NULL)
    order_id = models.PositiveIntegerField(null=True, blank=True)
    arrived_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        db_table = "db_order"
        constraints = [
            models.CheckConstraint(check=models.Q(total_price__gte=0), name="order_totalPrice_non_negative"),
            models.UniqueConstraint(fields=["customer", "order_id"], name="unique_order_id_per_customer"),
        ]

    def save(self, *args, **kwargs):
        if self.order_id is None:  # only set if not already defined

            last_order = Order.objects.filter(customer=self.customer).order_by('-order_id').first()
            self.order_id = 1 if not last_order else last_order.order_id + 1

        super().save(*args, **kwargs)


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