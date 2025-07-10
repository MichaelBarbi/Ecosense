from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

# Customer registration form
class CustomerRegistrationForm(forms.Form):

    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    fullName = forms.CharField(max_length=50)
    address = forms.CharField(max_length=50)
    city = forms.CharField(max_length=50)
    country = forms.CharField(max_length=50)
    postalCode = forms.CharField(max_length=20)
    province = forms.CharField(max_length=50)

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")


# Customer profile form
class CustomerProfileForm(forms.Form):

    username = forms.CharField(max_length=150, required=False, disabled=True)
    email = forms.EmailField(required=False, disabled=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="Update password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    fullName = forms.CharField(max_length=50, required=False, label="Full name")
    address = forms.CharField(max_length=50, required=False)
    city = forms.CharField(max_length=50, required=False)
    country = forms.CharField(max_length=50, required=False)
    postalCode = forms.CharField(max_length=20, required=False)
    province = forms.CharField(max_length=50, required=False)

    def clean_password(self):
        password = self.cleaned_data["password"]

        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        elif password and not confirm_password:
            self.add_error("confirm_password", "Confirm hasn't been entered")
        elif not password and confirm_password:
            self.add_error("password", "Password hasn't been entered")

        return cleaned_data


