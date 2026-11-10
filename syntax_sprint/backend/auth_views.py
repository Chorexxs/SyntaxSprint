"""Vistas de autenticación y sesiones."""

from __future__ import annotations

from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 300

User = get_user_model()


def _user_exists(email: str, username: str) -> bool:
    """Indica si el email o el nombre de usuario ya están registrados."""
    return (
        User.objects.filter(email__iexact=email).exists()
        or User.objects.filter(username__iexact=username).exists()
    )


def _add_password_errors(request: HttpRequest, password: str) -> bool:
    """Añade los errores de validación de contraseña y devuelve si hay alguno."""
    try:
        validate_password(password)
    except ValidationError as error:
        for message in error.messages:
            messages.error(request, message)
        return True
    return False


def _login_new_user(request: HttpRequest, username: str, password: str) -> None:
    """Autentica al usuario recién creado, si es posible."""
    user = auth.authenticate(request, username=username, password=password)
    if user is not None:
        auth.login(request, user)


@require_http_methods(["GET", "POST"])
def signup(request: HttpRequest) -> HttpResponse:
    """Registra un usuario nuevo y lo autentica si los datos son válidos."""
    if request.method != "POST":
        return render(request, "signup.html")

    email = (request.POST.get("email") or "").strip().lower()
    username = (request.POST.get("username") or "").strip()
    password = request.POST.get("password") or ""
    password2 = request.POST.get("password2") or ""

    if not all([email, username, password, password2]):
        return HttpResponseBadRequest("Faltan datos obligatorios.")

    if password != password2:
        messages.error(request, "Las contraseñas no coinciden.")
        return redirect("signup")

    if _user_exists(email, username):
        # Mensaje genérico para no revelar si la cuenta existe.
        messages.error(
            request,
            "No se pudo crear la cuenta. Revisa los datos o inicia sesión.",
        )
        return redirect("signup")

    if _add_password_errors(request, password):
        return redirect("signup")

    User.objects.create_user(username=username, email=email, password=password)
    _login_new_user(request, username, password)
    return redirect("index")


def _client_ip(request: HttpRequest) -> str:
    """Devuelve la IP del cliente para el límite de intentos."""
    return request.META.get("REMOTE_ADDR", "unknown")


@require_http_methods(["GET", "POST"])
def login(request: HttpRequest) -> HttpResponse:
    """Inicia sesión con un límite de intentos fallidos por IP."""
    if request.method != "POST":
        return render(request, "login.html")

    username = (request.POST.get("username") or "").strip()
    password = request.POST.get("password") or ""
    if not username or not password:
        return HttpResponseBadRequest("Faltan datos obligatorios.")

    cache_key = f"login-attempts:{_client_ip(request)}"
    attempts = cache.get(cache_key, 0)
    if attempts >= LOGIN_ATTEMPTS_LIMIT:
        messages.error(request, "Demasiados intentos. Inténtalo de nuevo más tarde.")
        return redirect("login")

    user = auth.authenticate(request, username=username, password=password)
    if user is None:
        cache.set(cache_key, attempts + 1, timeout=LOGIN_ATTEMPTS_TIMEOUT)
        messages.error(request, "Usuario o contraseña incorrectos.")
        return redirect("login")

    cache.delete(cache_key)
    auth.login(request, user)
    return redirect("index")


@login_required(login_url="login")
@require_POST
def logout(request: HttpRequest) -> HttpResponse:
    """Cierra la sesión del usuario autenticado (solo POST)."""
    auth.logout(request)
    return redirect("index")
