from django.views.generic import ListView, DeleteView
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from .models import *
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from order.models import Cart, CartItem
from user.views import customer_login_required, staff_login_required, technical_login_required
from order.models import Order
from django.contrib import messages
from .forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

@method_decorator(technical_login_required, name="dispatch")
class SensorItemDeleteView(SuccessMessageMixin, DeleteView):

    model = SensorItem
    template_name = "sensor/sensorItems.html"
    success_url = reverse_lazy("sensor_items")
    success_message = "The sensor item '%(name)s' was deleted successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message % {'name': self.object.get_registration_code()}

@technical_login_required
def sensorItemAdd(request):

    if request.method == "GET":

        try:

            # Get the form
            sensorItemAddForm = SensorItemAddForm()

            return render(
                request,
                template_name="sensor/sensorItemAdd.html",
                context={
                    "title": "Add Sensor Item",
                    "sensorItemAddForm": sensorItemAddForm
                }
            )

        except Exception as e:
            messages.error(request, f"The addition of a sensor item is not currently available: {str(e)}")
            return redirect("sensor_items")
        
    elif request.method == "POST":

        try:
            
            # Get the form
            sensorItemAddForm = SensorItemAddForm(request.POST)
            if not sensorItemAddForm.is_valid():
                raise ValueError("The form is invalid")
            
            sensorItemAddForm.save()

            messages.success(request, "The new sensor has been successfully created")
            return redirect("sensor_items")

        except Exception as e:
            messages.error(request, f"The new sensor item has not been created: {str(e)}")
            return redirect("sensor_items_add")

@technical_login_required
@require_POST
def sensorItemUpdateView(request, pk):
    try:
        sensorItem = get_object_or_404(SensorItem, pk=pk)
        sensorItemForm = SensorItemUpdateForm(request.POST)

        if not sensorItemForm.is_valid():
            raise ValueError("The form is invalid")

        plain_code = sensorItemForm.cleaned_data["registration_code"]

        for item in SensorItem.objects.exclude(pk=sensorItem.pk):
            decrypted = item.get_registration_code()
            if decrypted == plain_code:
                raise ValueError("Registration code already in use")

        sensorItem.registration_code = encrypt_value(plain_code)

        if sensorItemForm.cleaned_data["password"]:
            sensorItem.password = encrypt_value(sensorItemForm.cleaned_data["password"])

        if sensorItemForm.cleaned_data["api_key"]:
            sensorItem.api_key = encrypt_value(sensorItemForm.cleaned_data["api_key"])

        sensorItem.sensor = sensorItemForm.cleaned_data["sensor"]
        sensorItem.save()

        messages.success(request, "Sensor item updated successfully.")

    except Exception as e:
        messages.error(request, f"The sensor item has not been updated: {str(e)}")

    return redirect("sensor_items")


@method_decorator(technical_login_required, name="dispatch")
class SensorItemsListView(ListView):

    model = SensorItem
    template_name = "sensor/sensorItems.html"
    success_url = reverse_lazy("sensor_items")
    context_object_name = 'sensorItems'
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        get_params = self.request.GET.copy()
        if 'page' in get_params:
            get_params.pop('page')
        context['query_string'] = get_params.urlencode()

        context["title"] = "Sensor Items"
        context["sensorItemUpdateForm"] = SensorItemUpdateForm()
        context["sensorsNames"] = Sensor.objects.values_list("name", flat=True).distinct()

        return context

    
    def get_queryset(self):
        queryset = SensorItem.objects.select_related("sensor").all()

        # Get the params
        sensor_name_filter = self.request.GET.get("filter_sensor_name")
        sensor_select_filter = self.request.GET.get("filter_sensor")
        customer_filter = self.request.GET.get("filter_customer")
        is_registered = self.request.GET.get("is_registered")

        if sensor_name_filter:
            queryset = queryset.order_by("sensor__name")

        if sensor_select_filter:
            queryset = queryset.filter(sensor__name=sensor_select_filter)

        if customer_filter:
            queryset = queryset.filter(order__customer__user__username__icontains=customer_filter)

        if is_registered == "true":
            queryset = queryset.filter(is_registered=True)
        elif is_registered == "false":
            queryset = queryset.filter(is_registered=False)

        return queryset
    
    
    

@method_decorator(staff_login_required, name="dispatch")
class SensorDeleteView(SuccessMessageMixin, DeleteView):

    model = Sensor
    template_name = "sensor/sensors.html"
    success_url = reverse_lazy("sensors")
    success_message = "The sensor '%(name)s' was deleted successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message % {'name': self.object.name}

@staff_login_required
def addSensor(request):

    if not request.user.staff.is_sales:
        messages.error(request, "The staff user is not in sales group")
        return redirect("sensors")
    
    if request.method == "GET":

        try:
            
            # Get the form
            addSensorForm = AddSensorForm()

            return render(request, template_name="sensor/addSensor.html", context={
                "title": "Add Sensor",
                "addSensorForm": addSensorForm
            })

        except Exception as e:
            messages.error(request, f"The addition of a sensor is not currently available: {str(e)}")
            return redirect("sensors")
    
    elif request.method == "POST":
            
        try:

            # Get the from from the post request
            addSensorForm = AddSensorForm(request.POST, request.FILES)
            if not addSensorForm.is_valid():
                raise ValueError("The form is not valid")
            
            addSensorForm.save()

            messages.success(request, "The new sensor has been correctly created")
            return redirect("sensors")
            
        except Exception as e:
            messages.error(request, f"The new sensor has not been created: {str(e)}")
            return redirect("sensors_add")

# Update a sensor - Sales staff
@staff_login_required
@require_POST
def updateSensor(request, pk):
    
    try:
        
        if not request.user.staff.is_sales:
            raise ValueError("You don't have right permissions")
        
        # Get the sensor
        sensor = Sensor.objects.get(pk=pk)
        if not sensor:
            raise ValueError("The sensor doesn't exist")
        
        # Get the form 
        sensorForm = SensorForm(request.POST, request.FILES, instance=sensor)
        if not sensorForm.is_valid():
            raise ValueError(f"The form is not valid: {sensorForm.errors}")
        
        sensor = sensorForm.save(commit=False)
    
        # Se l'utente NON ha caricato una nuova immagine, mantieni quella vecchia
        if not request.FILES.get('image'):
            sensor.image = Sensor.objects.get(pk=pk).image

        sensor.save()
        sensorForm.save_m2m()
            
        messages.success(request, "The sensor has been successfully updated")

    except Exception as e:
        messages.error(request, f"The sensor has not been updated: {str(e)}")
    
    return redirect("sensors")

# View of all orders
@method_decorator(staff_login_required, name='dispatch')
class SensorListView(ListView):
    model = Sensor
    template_name = 'sensor/sensors.html'
    context_object_name = 'sensors'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Sensors"

        context["sensorForm"] = SensorForm(disabled=True)

        return context
    

    def get_queryset(self):
        return Sensor.objects.all().order_by('name')

# Add a new sensor type
@staff_login_required
def addSensortype(request): 

    if request.method == "GET":

        try:

            # Get the form
            sensorTypeForm = SensorTypeForm()

            return render(request, template_name="sensor/addSensorType.html", context={
                "title": "Add Sensor Type",
                "sensorTypeForm": sensorTypeForm
            })

        except Exception as e:
            messages.error(request, f"Adding a sensor type is not currently available: {str(e)}")
            return redirect("sensor_types")
        
    elif request.method == "POST":

        try:
            
            # Get the form
            sensorTypeForm = SensorTypeForm(request.POST)
            if not sensorTypeForm.is_valid():
                raise ValueError("The form is invalid")
            
            SensorType.objects.create(
                name = sensorTypeForm.cleaned_data["name"].capitalize(),
                description = sensorTypeForm.cleaned_data["description"] if sensorTypeForm.cleaned_data["description"] else "",
                symbol = sensorTypeForm.cleaned_data["symbol"] if sensorTypeForm.cleaned_data["symbol"] else ""
            )

            messages.success(request, "The new sensor type has been created correctly")

            return redirect("sensor_types")

        except Exception as e:
            messages.error(request, f"The new sensor type has not been created: {str(e)}")
            return redirect("sensor_types_add")

# Delete a sensor type
@method_decorator(staff_login_required, name='dispatch')
class SensorTypeDeleteView(SuccessMessageMixin, DeleteView):

    model = SensorType
    template_name = "sensor/sensorTypes.html"
    success_url = reverse_lazy("sensor_types")
    success_message = "The sensor type '%(name)s' was deleted successfully."

    def get_success_message(self, cleaned_data):
        return self.success_message % {'name': self.object.name}
    

# Update sensor type data
@staff_login_required
@require_POST
def sensorTypeUpdate(request, typeId):

    try:
        
        sensor_type = get_object_or_404(SensorType, pk=typeId)
        
        sensorTypeForm = SensorTypeForm(request.POST, instance=sensor_type)

        if not sensorTypeForm.is_valid():
            raise ValueError("The form is not valid")

        nameCap = sensorTypeForm.cleaned_data["name"].capitalize()

        sensor_type.name = nameCap
        sensor_type.description = sensorTypeForm.cleaned_data["description"]
        sensor_type.symbol = sensorTypeForm.cleaned_data["symbol"]

        sensor_type.save()

        messages.success(request, "The sensor type has been updated correctly")

    except Exception as e:
        messages.error(request, f"The sensor type has not been updated: {str(e)}")
    
    return redirect("sensor_types")

# View of all sensor types
@method_decorator(staff_login_required, name='dispatch')
class SensorTypeLsitView(ListView):

    model = SensorType
    template_name = 'sensor/sensorTypes.html'
    context_object_name = 'sensorTypes'

    def get_queryset(self):
        return SensorType.objects.all().order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Sensor Types"
        context["sensorTypeForm"] = SensorTypeForm()
        return context

# Recieve data from sensors
@csrf_exempt
def receive_sensor_data(request):

    if request.method == "POST":

        # Get the data from the request body
        data = json.loads(request.body)

        code = data.get("code")
        key = data.get("key")

        sensorItems = SensorItem.objects.filter(is_registered=True)
        sensor = None
        
        for sensoritem in sensorItems:

            try:

                sensorCode = sensoritem.get_registration_code()
                sensorKey = sensoritem.get_api_key()

                if sensorCode == code and sensorKey == key:                        
                    sensor = sensoritem

                    break
            except Exception:
                continue
        else:
            return JsonResponse({"error":"Unauthorized"}, status=403)
        
        group = sensor.group

        # Sensor values
        values = data.get("values", [])

        # Send data to the group channel via WebSocket
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"group_{group.group_id}",
            {
                "type": "send_sensor_data",
                "data": {
                    "sensor_id": sensor.pk,
                    "values": values
                }
            }
        )

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "POST only"}, status=400)

@customer_login_required
@require_POST
def addGroupToSensor(request):

    try:

        # Get the form
        selectGroupForm = SelectGroupForm(request.POST)

        if not selectGroupForm.is_valid():
            raise ValueError("The form is invalid")

        group = selectGroupForm.cleaned_data["group"]
        if not group:
            raise ValueError("The selected group is inexistent")
        
        # SensorId
        sensorId = int(request.POST["sensor"])
        sensoritem = SensorItem.objects.get(pk=sensorId)

        if not sensoritem:
            raise ValueError("The sensor selected is inexistent")
        
        sensoritem.group = group
        sensoritem.save()

    except Exception as e:
        messages.error(request, f"The sensor has not been added in the group: {str(e)}")

    return redirect("home")

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

            sensorItemToRegister.customer = request.user.customer

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
        sensorItems = SensorItem.objects.filter(is_registered=True, order__in=orders)

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
    
