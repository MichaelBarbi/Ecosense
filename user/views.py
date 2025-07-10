from django.contrib.auth.models import User
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from .models import *
from shipping.models import ShippingAddress
from django.db import IntegrityError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

def customer_login_required(view_func):
    return login_required(login_url='/login/')(view_func)

def staff_login_required(view_func):
    return login_required(login_url='/staff/login/')(view_func)


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
def registerView(request):

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

@customer_login_required
# Customer profile page
def profileView(request):

    # If the customer is not logged, he needs to sign in
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        return redirect("login")    


    if request.method == "POST":    
        
        form = CustomerProfileForm(request.POST)

        if form.is_valid():
            
            # Update user fields
            user = request.user

            user.first_name = form.cleaned_data["first_name"] if form.cleaned_data["first_name"] != "" else user.first_name
            user.last_name = form.cleaned_data["last_name"] if form.cleaned_data["last_name"] != "" else user.last_name

            password = form.cleaned_data.get("password")
            # The validation is already executed through is_valid() method
            if password:
                user.set_password(password)
                update_session_auth_hash(request, user)

            user.save()

            shipping = customer.shippingAddress

            shipping.fullName = form.cleaned_data["fullName"] if form.cleaned_data["fullName"] != "" else shipping.fullName
            shipping.address = form.cleaned_data["address"] if form.cleaned_data["address"] != "" else shipping.address
            shipping.city = form.cleaned_data["city"] if form.cleaned_data["city"] != "" else shipping.city
            shipping.province = form.cleaned_data["province"] if form.cleaned_data["province"] != "" else shipping.province
            shipping.postalCode = form.cleaned_data["postalCode"] if form.cleaned_data["postalCode"] != "" else shipping.postalCode
            shipping.country = form.cleaned_data["country"] if form.cleaned_data["country"] != "" else shipping.country

            shipping.save()

            messages.success(request, "Your profile was successfully updated")

            return redirect("profile")

        else:            
            form.add_error(None, f"Form is not valid")
            messages.error(request, "Your profile was not successfully updated")
    
    else:
        # Get all customer form data
        initial_data = {
            "username": request.user.username,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,

            "fullName": customer.shippingAddress.fullName,
            "address": customer.shippingAddress.address,
            "city": customer.shippingAddress.city,
            "province": customer.shippingAddress.province,
            "postalCode": customer.shippingAddress.postalCode,
            "country": customer.shippingAddress.country,
        }
        
        form = CustomerProfileForm(initial=initial_data)

    ctx = {
        "title": "Profile",
        "user": request.user,
        "form": form
    }

    return render(request, "user/profile.html", context=ctx)


@customer_login_required
def deleteAccountView(request):

    if request.method == "POST":

        try:
            user = request.user 
        
            user.delete()
            logout(request)

            return redirect("login")

        except Exception as e:
            messages.error(request, f"The account has not been deleted: {str(e)}")
            return redirect("profile")


    messages.error(request, "The account has not been deleted")
    return redirect("profile")
