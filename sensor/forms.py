from django import forms
from .models import SensorItem, SensorType

class SensorTypeForm(forms.ModelForm):

    class Meta:
        model = SensorType
        exclude = []

class RegisterSensorItemForm(forms.ModelForm):

    class Meta:
        model = SensorItem
        exclude = ['sensor', 'is_registered', 'api_key', 'order', 'customer', 'group']  

class ChangeSensorItemLabelForm(forms.ModelForm):

    class Meta:
        model = SensorItem
        fields = ['label']

class SelectGroupForm(forms.ModelForm):

    def __init__(self, *args, required=True, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = required

    class Meta:
        model = SensorItem
        fields = ["group"]
        labels = {
            "group": "Select the group with which to associate the chosen sensor"
        }
