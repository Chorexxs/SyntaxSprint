from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('get-python-gist/', views.get_python_gist, name='get_python_gist'),
    path("signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("settings", views.settings, name="settings"),
]
