from django import forms
from .models import Group

class AddGroupForm(forms.ModelForm):
    
    class Meta:
        model = Group     
        fields = ["name", "description"]

class ViewGroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["name", "description"]

