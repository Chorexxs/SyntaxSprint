from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    return render(request, "index.html")


def signup(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Ya existe este email")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "El nombre de usuario ya existe")
                return redirect(signup)
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()

                # Autentificando al usuario
                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)
                return redirect("/")

        else:
            messages.info(request, "La contraseña no coincide")
            return redirect("signup")

    else:
        return render(request, "signup.html")


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = auth.authenticate(
            username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("/")
        else:
            messages.info(request, "El Usuario no existe")
            return redirect("login")
    return render(request, "login.html")


def settings(request):
    return render(request, "settings.html")


@login_required(login_url="/")
def logout(request):
    auth.logout(request)
    return redirect("/")
