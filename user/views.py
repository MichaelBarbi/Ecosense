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
from functools import wraps

def customer_or_sales_login_required(view_func):
    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        is_customer = hasattr(user, 'customer')
        is_sales = hasattr(user, 'staff') and user.staff.is_sales

        if is_customer or is_sales:
            return view_func(request, *args, **kwargs)

        return redirect('/unauthorized/')
    
    return _wrapped_view

def customer_login_required(view_func):

    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):

        if hasattr(request.user, 'customer'):
            return view_func(request, *args, **kwargs)
        
        return redirect('/unauthorized/')  # oppure mostra messaggio
    return _wrapped_view

def staff_login_required(view_func):

    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):

        if hasattr(request.user, 'staff'):
            return view_func(request, *args, **kwargs)
        
        return redirect('/unauthorized/')
    return _wrapped_view

def sales_login_required(view_func):

    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):

        if hasattr(request.user, 'staff') and request.user.staff.is_sales:
            return view_func(request, *args, **kwargs)
        
        return redirect("/unauthorized/")
    return _wrapped_view

def technical_login_required(view_func):

    @wraps(view_func)
    @login_required(login_url='/login/')
    def _wrapped_view(request, *args, **kwargs):

        if hasattr(request.user, 'staff') and request.user.staff.is_technical:
            return view_func(request, *args, **kwargs)
        
        return redirect("/unauthorized/")
    return _wrapped_view

def unauthorized(request):
    return render(request, 'unauthorized.html', {'title': 'Unauthorized access'})

# Customer login
def loginView(request):

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            # Remember me
            if not request.POST.get("remember"):
                request.session.set_expiry(0)  # Session expires after closing browser
            else:
                request.session.set_expiry(604800)  # 1 week

            login(request, user)

            if hasattr(user, 'customer') or hasattr(user, 'staff'):
                return redirect('home')
            else:
                logout(request)
                return redirect('login')

    else:

        # User already authenticated
        if request.user.is_authenticated:

            user = request.user
            
            if hasattr(user, 'customer') or hasattr(user, 'staff'):
                return redirect('home')
            else:
                logout(request)
                return redirect('login')

        form = AuthenticationForm()

    ctx = {
        "title": "Login",
        "form": form
    }

    return render(request, template_name="login.html", context=ctx)

# Register a new customer
def registerView(request):

    # If the user is already logged in
    if request.user.is_authenticated:
        if not hasattr(request.user, 'customer') and not hasattr(request.user, 'staff'):
            logout(request)
        return redirect('home') 

    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            try:

                # Extract the data
                username = form.cleaned_data['username']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]

                full_name = form.cleaned_data['full_name']
                address = form.cleaned_data['address']
                city = form.cleaned_data['city']
                province = form.cleaned_data['province']
                postal_code = form.cleaned_data['postal_code']
                country = form.cleaned_data['country']

                # Validate the password
                validate_password(password)

                # Create the user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                # Set customer and shippinAddress
                customer = Customer.objects.create(user=user)
                ShippingAddress.objects.create(
                    customer=customer,
                    full_name=full_name,
                    address=address,
                    city=city,
                    province=province,
                    postal_code=postal_code,
                    country=country
                )

                login(request, user)
                return redirect("home")

            except ValidationError as e:
                form.add_error('password', e)

            except IntegrityError as e:
                form.add_error(None, f"Integrity error: {str(e)}")

            except Exception as e:
                form.add_error(None, f"Generic error: {str(e)}")

    else:
        form = CustomerRegistrationForm()

    return render(request, "register.html", {"form": form, "title": "Register"})

def getTypeOfUser(request):
    
    if not request or not hasattr(request, "user"):
        return None, None
    
    user = request.user
    
    if hasattr(user, "customer"):
        return user.customer, "customer"
    elif hasattr(user, "staff"):
        return user.staff, "staff"
    else:
        return None, None

# Logout
def logoutView(request):

    logout(request)
    return redirect("home")

@login_required
# User profile page
def profileView(request):

    userLogged, userType = getTypeOfUser(request)

    if not userLogged or not userType:
        return redirect("login")

    if userType == "customer":

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

                shipping = userLogged.shippingAddress

                shipping.full_name = form.cleaned_data["full_name"] if form.cleaned_data["full_name"] != "" else shipping.full_name
                shipping.address = form.cleaned_data["address"] if form.cleaned_data["address"] != "" else shipping.address
                shipping.city = form.cleaned_data["city"] if form.cleaned_data["city"] != "" else shipping.city
                shipping.province = form.cleaned_data["province"] if form.cleaned_data["province"] != "" else shipping.province
                shipping.postal_code = form.cleaned_data["postal_code"] if form.cleaned_data["postal_code"] != "" else shipping.postal_code
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

                "full_name": userLogged.shippingAddress.full_name,
                "address": userLogged.shippingAddress.address,
                "city": userLogged.shippingAddress.city,
                "province": userLogged.shippingAddress.province,
                "postal_code": userLogged.shippingAddress.postal_code,
                "country": userLogged.shippingAddress.country,
            }
            
            form = CustomerProfileForm(initial=initial_data)

    elif userType == "staff":

        if request.method == "GET":

            initial_data = {
                "username": request.user.username,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name
            }
            
            form = StaffProfileForm(initial=initial_data)

        elif request.method == "POST":

            form = StaffProfileForm(request.POST)

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

                messages.success(request, "Your profile was successfully updated")

                return redirect("profile")

            else:            
                form.add_error(None, f"Form is not valid")
                messages.error(request, "Your profile was not successfully updated")

    ctx = {
        "title": "Profile",
        "user": request.user,
        "form": form
    }

    return render(request, "user/profile.html", context=ctx)

@login_required
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
