from django.shortcuts import render, redirect
from django.contrib.auth import logout
from sensor.models import SensorItem
from group.models import *
from sensor.forms import SelectGroupForm

# Home page
def home(request):

    title = "Home"

    context = {
        "title": title
    }

    if request.user.is_authenticated:
        
        # Customer dashboard
        if hasattr(request.user, 'customer'):
            
            # Get all customer sensorItems that are not used in any group
            sensorItemsNotUsed = SensorItem.objects.filter(customer=request.user.customer, group=None).order_by("registration_code")

            # Get all customer groups
            groups = Group.objects.filter(customer=request.user.customer).order_by("name")

            selectGroupForm = SelectGroupForm()

            context = {
                "title": title,
                "sensorItemsNotUsed": sensorItemsNotUsed,
                "groups": groups,
                "selectGroupForm": selectGroupForm
            }

        elif hasattr(request.user, 'staff'):
            pass

        else:
            logout(request)
            return redirect("home")
        
    return render(request, 'home.html', context=context)
