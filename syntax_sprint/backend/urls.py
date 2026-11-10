from django.urls import path

from . import auth_views, result_views, snippet_views, views

urlpatterns = [
    path("", views.index, name="index"),
    path(
        "get_python_function",
        snippet_views.get_python_function,
        name="get_python_function",
    ),
    path("signup", auth_views.signup, name="signup"),
    path("login", auth_views.login, name="login"),
    path("logout", auth_views.logout, name="logout"),
    path("profile", result_views.profile, name="profile"),
    path(
        "save_typing_test_result",
        result_views.save_typing_test_result,
        name="save_typing_test_result",
    ),
]
