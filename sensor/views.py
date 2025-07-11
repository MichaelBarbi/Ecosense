from django.shortcuts import render
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from .models import *

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
