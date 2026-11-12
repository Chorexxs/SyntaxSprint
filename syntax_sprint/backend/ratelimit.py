"""Límites de peticiones por IP sobre una caché compartida opcional."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.cache import InvalidCacheBackendError, caches
from django.core.cache.backends.base import BaseCache
from django.db import DatabaseError
from django.http import HttpRequest

logger = logging.getLogger(__name__)

SNIPPET_LIMIT = 120
SNIPPET_WINDOW_SECONDS = 60
ADMIN_LOGIN_LIMIT = 5
ADMIN_LOGIN_WINDOW_SECONDS = 300
ADMIN_LOGIN_PATH = "/admin/login/"
ADMIN_2FA_LIMIT = 5
ADMIN_2FA_WINDOW_SECONDS = 300


def _cache(alias: str | None = None) -> BaseCache:
    """Devuelve la caché del alias indicado, con fallback a la local."""
    name = alias or settings.RATE_LIMIT_CACHE_ALIAS
    try:
        return caches[name]
    except InvalidCacheBackendError:
        logger.error("Alias de caché desconocido (%s); se usa default", name)
        return caches["default"]


def _bump_counter(cache: BaseCache, key: str, window_seconds: int) -> int:
    """Suma uno al contador y devuelve el valor resultante."""
    if cache.add(key, 1, timeout=window_seconds):
        return 1
    try:
        return cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=window_seconds)
        return 1


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
    alias: str | None = None,
) -> bool:
    """Cuenta la petición y devuelve ``True`` si supera el límite.

    ``alias`` permite usar una caché distinta a la de autenticación. Si la caché
    no está disponible se permite la petición y se registra el fallo: un rate
    limit roto no debe bloquear el sitio.
    """
    key = rate_limit_key(request, scope)
    try:
        count = _bump_counter(_cache(alias), key, window_seconds)
    except DatabaseError:
        logger.exception("Caché de rate limiting no disponible")
        return False
    return count > limit


def reset_rate_limit(request: HttpRequest, scope: str) -> None:
    """Reinicia el contador tras una operación correcta."""
    try:
        _cache().delete(rate_limit_key(request, scope))
    except DatabaseError:
        logger.exception("No se pudo reiniciar el contador de rate limiting")


def get_counter(key: str) -> int:
    """Devuelve el valor del contador (0 si no existe o falla la caché)."""
    try:
        return _cache().get(key, 0)
    except DatabaseError:
        logger.exception("No se pudo leer el contador de intentos")
        return 0


def increment_counter(key: str, window_seconds: int) -> None:
    """Suma uno al contador, creándolo con la ventana indicada."""
    try:
        _bump_counter(_cache(), key, window_seconds)
    except DatabaseError:
        logger.exception("No se pudo incrementar el contador de intentos")


def reset_counter(key: str) -> None:
    """Elimina el contador."""
    try:
        _cache().delete(key)
    except DatabaseError:
        logger.exception("No se pudo reiniciar el contador de intentos")
