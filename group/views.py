from django.shortcuts import render, redirect
from user.views import customer_login_required
from django.views.decorators.http import require_POST
from .forms import AddGroupForm, ViewGroupForm
from django.contrib import messages
from .models import Group
from sensor.models import SensorItem

# GET => View the group page
# POST (save, delete):
#   - Save the new data of the group
#   - Delete the group
@customer_login_required
def groupView(request, group_id):

    title = "Group " + str(group_id)

    try:

        # Get the group
        group = Group.objects.get(customer=request.user.customer, group_id=group_id)

    except Exception as e:
        messages.error(request, "The group does not exist.")
        return redirect("home")

    if request.method == "GET":

        viewGroupForm = ViewGroupForm(instance=group)
        sensoritems = SensorItem.objects.filter(customer=request.user.customer, group=group)

        return render(request, "group/view_group.html", {
            "title": title,
            "group": group,
            "viewGroupForm": viewGroupForm,
            "sensoritems": sensoritems
        })

    elif request.method == "POST":

        action = request.POST["action"]

        # If the customer pressed Delete button
        if action == "delete":

            try:

                group.delete()

                messages.success(request, "The group has been deleted")
                return redirect("home")
            
            except Exception as e:

                messages.error(request, f"The group n. {group_id} has not been deleted: {str(e)}")
                return redirect("groups:manage", group_id=group_id)

        # If the customer pressed Save button
        elif action == "save":

            groupForm = ViewGroupForm(request.POST, instance=group)

            if groupForm.is_valid():

                groupForm.save()
                messages.success(request, f"The group n. {group_id} has been correctly updated")
            else:
                messages.error(request, "The group form is invalid")

            return redirect("groups:manage", group_id=group_id)

        else:
            messages.error(request, "Invalid action")
            return redirect("groups:manage", group_id=group_id)


@customer_login_required
@require_POST
def removeSensorFromGroup(request, group_id):

    try:
        
        # Get the sensor Id
        sensorPK = int(request.POST["sensorItem"])

        if not sensorPK:
            raise ValueError("The sensor is invalid")
        
        # Get the sensor object
        sensoritem = SensorItem.objects.get(pk=sensorPK, customer=request.user.customer)
        if not sensoritem:
            raise ValueError("The sensor doesn't exist")
        
        sensoritem.group = None
        sensoritem.save()

        messages.success(request, "The sensor has been removed correctly")

    except Exception as e:
        messages.error(request, f"The sensor has not been removed from the group: {str(e)}")

    return redirect("groups:manage", group_id)

@customer_login_required
def addGroupView(request):

    title = "Add group"

    if request.method == "GET":

        try:
            # Get the form to add a group
            addGroupForm = AddGroupForm()

            return render(request, template_name="group/add_group.html", context={
                "title": title,
                "addGroupForm": addGroupForm
            })
        
        except Exception as e:

            messages.error(request, f"{str(e)}")
            return redirect("home")
        
    elif request.method == "POST":

        try:
            
            # Get the form
            addGroupForm = AddGroupForm(request.POST)

            if not addGroupForm.is_valid():
                raise ValueError("Data are invalid")
            
            Group.objects.create(
                name = addGroupForm.cleaned_data["name"],
                description = addGroupForm.cleaned_data["description"] if addGroupForm.cleaned_data["description"] else "",
                customer = request.user.customer
            )

            messages.success(request, f"The group '{addGroupForm.cleaned_data["name"]}' has been created")

            return redirect("home")

        except Exception as e:

            messages.error(request, str(e))
            return redirect("groups:add_group")
