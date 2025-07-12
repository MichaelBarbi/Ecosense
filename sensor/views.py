from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from order.models import Cart, CartItem

class catalogListView(ListView):

    model = Sensor
    template_name = "sensor/catalog.html"
    context_object_name = "sensors"

    # This method is used to add extra data to the context 
    def get_context_data(self, **kwargs):
        
        # Get the default context provided by ListView
        context = super().get_context_data(**kwargs)
        
        context["title"] = "Catalog"

        # Add all available sensor types (used to generate filter checkboxes in the UI)
        context["sensor_types"] = SensorType.objects.all()

        return context
    
    # This method is used to customize the list of objects that will be shown
    def get_queryset(self):

        # Get the default queryset (Sensor.objects.all())
        queryset = super().get_queryset().filter(quantity__gt=0)

        # Get the list of selected sensor type IDs from the GET parameters
        type_ids = self.request.GET.getlist("types")

        if type_ids:
            # Only return sensors that have at least one of the selected types
            queryset = queryset.filter(types__id__in=type_ids).distinct()

        return queryset


# Add a sensor in the cart
@require_POST
def add_to_cart(request):

    if request.user.is_authenticated and request.user.customer:
        try:
            sensor_id = request.POST.get('sensor_id')
            quantity = int(request.POST.get('quantity', 1))

            sensor = get_object_or_404(Sensor, id=sensor_id)

            sensorQuantity = sensor.quantity

            if quantity > sensorQuantity:
                raise ValueError(f": Quantity left: {sensorQuantity}")
            
            if quantity < 1 or quantity > 999:
                raise ValueError(f": The quantity value inserted is not valid")

            # Retrieve or create the user cart
            cart, created = Cart.objects.get_or_create(customer=request.user.customer)

            # Retrieve or create the new CartItem
            item, created = CartItem.objects.get_or_create(cart=cart, sensor=sensor)

            if not created:
                item.quantity += quantity
            else:
                item.quantity = quantity

            item.save()

            total_items = sum(i.quantity for i in cart.cartItems.all())
            
            return JsonResponse({
                'status': 'success', 
                'total_items': total_items,
                "message": "The cart has been updated"
            })
        
        except Exception as e:

            return JsonResponse({
                'status': 'danger',
                "message": f"The cart has not been updated {str(e)}"
            })
    else:

        return JsonResponse({
            'status': 'unauthenticated',
            'redirect_url': '/login/'
        })
    
