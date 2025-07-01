from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import CustomerRegistrationForm
from .models import *
from shipping.models import ShippingAddress
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


# Customer login
def loginView(request):

    if request.method == "POST":
        
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():

            user = form.get_user()

            # Remember me
            if not request.POST.get("remember"):
                request.session.set_expiry(0) # Session expires after closing the browser
            else:
                request.session.set_expiry(604800) 

            login(request, user)
            return redirect("home")

    else:

        # If user is alreasy logged, redirect him to home
        if request.user.is_authenticated:
            return redirect("home")

        form = AuthenticationForm()

    ctx = {
        "title": "Login",
        "form": form
    }

    return render(request, template_name="login.html", context=ctx)

# Customer register 
def register(request):

    if request.method == "POST":

        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():

            try:
                
                # Extract the cleaned data
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]

                fullName = form.cleaned_data['fullName']
                address = form.cleaned_data['address']
                city = form.cleaned_data['city']
                province = form.cleaned_data['province']
                postalCode = form.cleaned_data['postalCode']
                country = form.cleaned_data['country']

                # Password validation with native auth validators
                try:
                    validate_password(password, user=None)
                except ValidationError as e:
                    form.add_error('password', e)
                    raise Exception("Password validation failed")

                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                # Cretae the customer and his shipping address
                customer = Customer.objects.create(user=user)
                ShippingAddress.objects.create(
                    customer=customer,
                    fullName=fullName,
                    address=address,
                    city=city,
                    province=province,
                    postalCode=postalCode,
                    country=country
                )

                login(request, user)
                return redirect("home")

            except IntegrityError as e:
                form.add_error(None, f"Integrity error: {str(e)}")

            except Exception as e:
                form.add_error(None, f"Generic error: {str(e)}")
    else:

        # If user is alreasy logged, redirect him to home
        if request.user.is_authenticated:
            return redirect("home")

        form = CustomerRegistrationForm()

    return render(request, "register.html", {"form": form})

# Logout
def logoutView(request):

    logout(request)
    return redirect("home")


