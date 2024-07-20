from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("singup", views.singup, name="singup"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("settings", views.settings, name="settings"),
]
