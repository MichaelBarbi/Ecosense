from django import forms
from .models import *
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
import re

class SensorItemAddForm(forms.ModelForm):

    class Meta:
        model = SensorItem
        fields  = ["registration_code", "password", "api_key", "sensor"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add the regex validator for the registration code
        self.fields["registration_code"].validators.append(
            RegexValidator(
                regex=r'^[A-Za-z0-9]{5}-[A-Z0-9]{5}-[A-Za-z0-9]{5}$',
                message='Registration code must be in format: XXXXX-XXXXX-XXXXX (alphanumeric only)',
                code='invalid_format'
            )
        )

    def clean_registration_code(self):
        registration_code = self.cleaned_data.get("registration_code").upper()

        if not registration_code:
            return registration_code
        
        # Verify uniqueness (by decrypting all existing codes)
        existing_sensor_items = SensorItem.objects.all()

        for sensor_item in existing_sensor_items:

            decrypted_code = sensor_item.get_registration_code()
            
            if decrypted_code and decrypted_code.upper() == registration_code:
                raise ValidationError("This registration code is already in use")
        
        return registration_code
    
    def clean_password(self):
        password = self.cleaned_data.get("password")

        if password:
            
            try:

                # I use the django password validator
                validate_password(password)

            except ValidationError as e:
                raise ValidationError(e.messages)
            
        return password
    
    def clean_api_key(self):
        api_key = self.cleaned_data.get('api_key')
        
        if not api_key:
            return api_key
        
        # Verify uniqueness (by decrypting all existing api keys)
        existing_sensor_items = SensorItem.objects.all()

        for sensor_item in existing_sensor_items:

            decrypted_api_key = sensor_item.get_api_key()

            if decrypted_api_key and decrypted_api_key == api_key:
                raise ValidationError("This API key is already in use.")
        
        # Validate the api key with the same validators of the password
        try:
            validate_password(api_key)
        except ValidationError as e:
            raise ValidationError(e.messages)
        
        return api_key
    
    def clean_sensor(self):
        sensor = self.cleaned_data.get('sensor')
        
        if not sensor:
            raise ValidationError("Sensor is required.")
        
        return sensor

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
