from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('get_python_function', views.get_python_function,
         name='get_python_function'),
    path("signup", views.signup, name="signup"),
    path("login", views.login, name="login"),
    path("logout", views.logout, name="logout"),
    path("profile", views.profile, name="profile"),
]
