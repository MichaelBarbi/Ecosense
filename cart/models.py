from django.db import models
from user.models import Customer
from django.core.validators import MinValueValidator
from sensor.models import Sensor

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
