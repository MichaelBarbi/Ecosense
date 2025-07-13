from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):

    def __init__(self, *args, disabled=False, required=True, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.disabled = disabled
            field.required = required


    class Meta:
        model = ShippingAddress
        exclude = ['customer']  # Exclude the customer
