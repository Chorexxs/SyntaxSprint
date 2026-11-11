"""Límites de peticiones por IP sobre la caché de Django."""

from __future__ import annotations

from django.core.cache import cache
from django.http import HttpRequest

SNIPPET_LIMIT = 120
SNIPPET_WINDOW_SECONDS = 60
ADMIN_LOGIN_LIMIT = 5
ADMIN_LOGIN_WINDOW_SECONDS = 300
ADMIN_LOGIN_PATH = "/admin/login/"


def client_ip(request: HttpRequest) -> str:
    """Devuelve la IP del cliente.

    Gunicorn reescribe ``REMOTE_ADDR`` con ``X-Forwarded-For`` cuando la
    petición llega de un proxy de confianza (ver ``forwarded_allow_ips``).
    """
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limit_key(request: HttpRequest, scope: str) -> str:
    """Clave de caché del contador para un ámbito e IP."""
    return f"ratelimit:{scope}:{client_ip(request)}"


def is_rate_limited(
    request: HttpRequest,
    scope: str,
    limit: int,
    window_seconds: int,
) -> bool:
    """Cuenta la petición y devuelve ``True`` si supera el límite."""
    key = rate_limit_key(request, scope)
    if cache.add(key, 1, timeout=window_seconds):
        return False
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=window_seconds)
        return False
    return count > limit


def reset_rate_limit(request: HttpRequest, scope: str) -> None:
    """Reinicia el contador tras una operación correcta."""
    cache.delete(rate_limit_key(request, scope))
