from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from common.signals import update_total
from models import CartItem

@receiver(pre_save, sender=CartItem)
def update_cart_item_amount(sender, instance, **kwargs):
    instance.amount = instance.quantity * instance.sensor.price

# Cart Item 
@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_cart_total_price(sender, instance, **kwargs):
    update_total(instance, related_name="cartItems", parent_attr="cart", total_field="total_price")