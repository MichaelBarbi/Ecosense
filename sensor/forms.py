from django import forms
from .models import SensorItem

class RegisterSensorItemForm(forms.ModelForm):

    class Meta:
        model = SensorItem
        exclude = ['sensor', 'is_registered', 'api_key', 'order']  

class ChangeSensorItemLabelForm(forms.ModelForm):

    class Meta:
        model = SensorItem
        fields = ['label']
