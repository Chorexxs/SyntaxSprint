import json
import math

from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import TypingTestResult
from .snippets import pick_snippet

LOGIN_ATTEMPTS_LIMIT = 5
LOGIN_ATTEMPTS_TIMEOUT = 300

User = get_user_model()


# Create your views here.


@require_http_methods(["GET", "POST"])
def get_python_function(request) -> JsonResponse:
    """Devuelve un fragmento de código aleatorio del lenguaje solicitado."""
    if request.method == "POST":
        try:
            data = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Cuerpo JSON inválido"}, status=400)
        language = data.get("language", "python") if isinstance(data, dict) else "python"
    else:
        language = "python"

    if not isinstance(language, str):
        language = "python"

    return JsonResponse(pick_snippet(language))


def index(request):
    """Renderiza la portada pública del test."""
    return render(request, "index.html")


@require_http_methods(["GET", "POST"])
def signup(request):
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

    if User.objects.filter(email__iexact=email).exists() or User.objects.filter(
        username__iexact=username
    ).exists():
        # Mensaje genérico para no revelar si la cuenta existe.
        messages.error(
            request,
            "No se pudo crear la cuenta. Revisa los datos o inicia sesión.",
        )
        return redirect("signup")

    try:
        validate_password(password)
    except ValidationError as error:
        for message in error.messages:
            messages.error(request, message)
        return redirect("signup")

    User.objects.create_user(
        username=username, email=email, password=password
    )
    user_login = auth.authenticate(
        request, username=username, password=password
    )
    if user_login is not None:
        auth.login(request, user_login)
    return redirect("index")


def _client_ip(request) -> str:
    """Devuelve la IP del cliente para el límite de intentos."""
    return request.META.get("REMOTE_ADDR", "unknown")


@require_http_methods(["GET", "POST"])
def login(request):
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
        messages.error(
            request, "Demasiados intentos. Inténtalo de nuevo más tarde."
        )
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
def logout(request):
    """Cierra la sesión del usuario autenticado (solo POST)."""
    auth.logout(request)
    return redirect("index")


@login_required(login_url="login")
@require_POST
def save_typing_test_result(request):
    """Guarda un resultado validando tipo y rango en el servidor."""
    try:
        data = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Cuerpo JSON inválido"}, status=400)

    if not isinstance(data, dict):
        return JsonResponse({"error": "Datos no válidos"}, status=400)

    try:
        wpm = float(data["wpm"])
        accuracy = float(data["accuracy"])
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "Datos no válidos"}, status=400)

    if not math.isfinite(wpm) or not 0 <= wpm <= 400:
        return JsonResponse({"error": "WPM fuera de rango"}, status=400)
    if not math.isfinite(accuracy) or not 0 <= accuracy <= 100:
        return JsonResponse({"error": "Precisión fuera de rango"}, status=400)

    TypingTestResult.objects.create(
        user=request.user, wpm=wpm, accuracy=accuracy
    )
    return JsonResponse({"message": "Resultado guardado exitosamente"})


@login_required(login_url="login")
def profile(request):
    """Muestra el historial y los promedios del usuario autenticado."""
    results = TypingTestResult.objects.filter(
        user=request.user
    ).order_by("-date")
    stats = results.aggregate(
        avg_wpm=Avg("wpm"), avg_accuracy=Avg("accuracy")
    )

    context = {
        "results": results,
        "avg_wpm": stats["avg_wpm"] or 0,
        "avg_accuracy": stats["avg_accuracy"] or 0,
    }
    return render(request, "profile.html", context)
