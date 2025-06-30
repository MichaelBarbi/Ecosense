from django.shortcuts import render

# Home page
def home(request):
    context = {
        "title": "Home"
    }
    return render(request, 'home.html', context=context)
