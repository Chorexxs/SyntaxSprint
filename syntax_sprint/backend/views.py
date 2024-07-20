from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

# Create your views here.


def index(request):
    return render(request, "index.html")


def singup(request):
    if request.method == "POST":
        email = request.POST["email"]
        name = request.POST["name"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            pass
        else:
            messages.info(request, "La contraseña no coincide")
            return redirect("singup")

    else:
        return render(request, "singup.html")


def login(request):
    return render(request, "login.html")


def settings(request):
    return render(request, "settings.html")


def logout(request):
    pass
