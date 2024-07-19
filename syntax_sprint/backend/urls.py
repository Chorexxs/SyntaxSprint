from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("settings", views.settings, name="settings"),
]
