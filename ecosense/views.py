from django.shortcuts import render

# Home page
def home(request):
    context = {
        "title": "Home"
    }
    return render(request, 'home.html', context=context)

# Customer login page
def login(request):
    ctx = {
        "title": "Login"
    }

    return render(request, template_name="login.html", context=ctx)

# Customer register page
def register(request):
    ctx = {
        "title": "Register"
    }

    return render(request, template_name="register.html", context=ctx)