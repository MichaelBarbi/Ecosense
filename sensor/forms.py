from django import forms
from .models import *

class SensorItemAddForm(forms.ModelForm):

    class Meta:
        model = SensorItem
        fields  = ["registration_code", "password", "api_key", "sensor"]

class SensorItemUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].required = False
        self.fields['api_key'].required = False

    class Meta:
        model = SensorItem
        fields  = ["registration_code", "password", "api_key", "sensor"]

class AddSensorForm(forms.ModelForm):

    class Meta:
        model = Sensor
        exclude = ["quantity"]

class SensorForm(forms.ModelForm):

    class Meta:
        model = Sensor
        exclude = []

    def __init__(self, *args, disabled=False, **kwargs):
        super().__init__(*args, **kwargs)

        if disabled:
            self.fields['quantity'].disabled = True

    def clean_quantity(self):
        if self.fields['quantity'].disabled and self.instance:
            return self.instance.quantity
        return self.cleaned_data['quantity']

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
