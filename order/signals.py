from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import OrderItem, CartItem

# Function to update total_price field for cart and order 
def update_total(instance, related_name, parent_attr, total_field):
    parent = getattr(instance, parent_attr)
    items = getattr(parent, related_name).select_related("sensor").all()
    total = sum(item.quantity * item.sensor.price for item in items)
    setattr(parent, total_field, total)
    parent.save(update_fields=[total_field])

# Pre-save to update the amount field before saving
@receiver(pre_save, sender=OrderItem)
def update_order_item_amount(sender, instance, **kwargs):
    instance.amount = instance.quantity * instance.sensor.price

@receiver(pre_save, sender=CartItem)
def update_cart_item_amount(sender, instance, **kwargs):
    instance.amount = instance.quantity * instance.sensor.price


# Post-save and Post-delete to update the total_price field

# Order Item
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total_price(sender, instance, **kwargs):
    update_total(instance, related_name="orderItems", parent_attr="order", total_field="total_price")

# Cart Item 
@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_cart_total_price(sender, instance, **kwargs):
    update_total(instance, related_name="cartItems", parent_attr="cart", total_field="total_price")
