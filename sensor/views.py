from django.views.generic import ListView
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from order.models import Cart, CartItem
from user.views import customer_login_required
from order.models import Order
from django.contrib import messages
from .forms import *


#Update label of a registered sensor
@customer_login_required
@require_POST
def sensorLabelUpdateView(request, pk):

    try:
        
        # Get the form with data
        changeSensorItemLabelForm = ChangeSensorItemLabelForm(request.POST)

        if not changeSensorItemLabelForm.is_valid():
            raise ValueError("The label value is invalid")
        
        label = changeSensorItemLabelForm.cleaned_data["label"] if changeSensorItemLabelForm.cleaned_data["label"] else ""

        sensorItem = SensorItem.objects.get(pk=pk)
        sensorItem.label = label

        sensorItem.save()

        messages.success(request, "The label has been changed")
        return redirect("registered_sensors")

    except Exception as e:
        
        messages.error(request, f"The label has not been changed: {str(e)}")
        return redirect("registered_sensors")

# Register a sensor
@customer_login_required
def registerSensorView(request):

    if request.method == "GET":

        try:
            
            # Form
            registerSensorItemForm = RegisterSensorItemForm()   

            return render(request, template_name="sensor/register-sensor.html", context={
                "title": "Register a sensor",
                "registerSensorItemForm": registerSensorItemForm
            })        

        except Exception as e:
            messages.error(request, f"Failed to load the page: {str(e)}")
            return redirect("registered_sensors")
        
    elif request.method == "POST":

        try:

            # Obtain the form with data
            registerSensorItemForm = RegisterSensorItemForm(request.POST)
            if not registerSensorItemForm.is_valid():
                raise ValueError("The information inserted are invalid")

            # Obtain all orders of the current user
            orders = Order.objects.filter(customer=request.user.customer)

            # I retrieve all sensor items still not registered and that belongs to orders of the customer
            sensorItems = SensorItem.objects.filter(is_registered=False, order__in=orders)

            sensorItemToRegister = None
            
            for sensor in sensorItems:

                try:

                    reg_code = sensor.get_registration_code()
                    pwd = sensor.get_password()

                    if reg_code == registerSensorItemForm.cleaned_data["registration_code"] and pwd == registerSensorItemForm.cleaned_data["password"]:                        
                        sensorItemToRegister = sensor

                        break
                except Exception:
                    continue
            else:
                messages.error(request, "Sensor not found")
                return redirect("register_sensor")

             
            sensorItemToRegister.is_registered = True
            sensorItemToRegister.label = registerSensorItemForm.cleaned_data["label"] if registerSensorItemForm.cleaned_data["label"] else ""

            sensorItemToRegister.save()

            messages.success(request, f"The sensor {registerSensorItemForm.cleaned_data["registration_code"]} has been registered")

            return redirect('registered_sensors')

        except Exception as e:
            messages.error(request, f"Failed to register a new sensor: {str(e)}")
            return redirect("register_sensor")


# View of all customer registered sensors
@method_decorator(customer_login_required, name='dispatch')
class CustomerRegisteredSensorsListView(ListView):

    model = SensorItem
    template_name = 'sensor/registered-sensors.html'
    context_object_name = 'sensorItems'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context["title"] = "Registered sensors"
        context["changeSensorItemLabelForm"] = ChangeSensorItemLabelForm()

        return context

    def get_queryset(self):   

        # Obtain all orders of the current user
        orders = Order.objects.filter(customer=self.request.user.customer)    

        # All sensor items registered of the customer
        sensorItems = SensorItem.objects.filter(is_registered=True, order__in=orders).order_by('-registration_code')

        for sensor in sensorItems:

            sensor.registration_code = sensor.get_registration_code()
            
        return sensorItems

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
    
