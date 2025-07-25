from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

from common.signals import update_total
from .models import OrderItem

# Pre-save to update the amount field before saving
@receiver(pre_save, sender=OrderItem)
def update_order_item_amount(sender, instance, **kwargs):
    instance.amount = instance.quantity * instance.sensor.price

# Order Item
@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total_price(sender, instance, **kwargs):
    update_total(instance, related_name="orderItems", parent_attr="order", total_field="total_price")
