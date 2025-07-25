# Function to update total_price field for cart and order 
def update_total(instance, related_name, parent_attr, total_field):
    parent = getattr(instance, parent_attr)
    items = getattr(parent, related_name).select_related("sensor").all()
    total = sum(item.quantity * item.sensor.price for item in items)
    setattr(parent, total_field, total)
    parent.save(update_fields=[total_field])