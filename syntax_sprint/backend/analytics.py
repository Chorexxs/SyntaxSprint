"""Registro y métricas de producto (spec 011)."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import DatabaseError
from django.db.models import Count, Q
from django.utils import timezone

from .models import SnippetRequest, TypingTestResult

logger = logging.getLogger(__name__)

DEFAULT_WINDOW_DAYS = 28
DEFAULT_RETENTION_DAYS = 90
PURGE_CACHE_KEY = "analytics:last-purge"
PURGE_CACHE_TIMEOUT = 86400


def record_snippet_request(language: str, status_code: int, started: float) -> None:
    """Guarda el evento de una petición sin romperla ante un fallo de base de datos."""
    duration_ms = max(int((time.monotonic() - started) * 1000), 0)
    try:
        SnippetRequest.objects.create(
            language=(language or "unknown")[:32],
            status_code=status_code,
            duration_ms=duration_ms,
        )
        maybe_purge_snippet_requests()
    except DatabaseError:
        logger.exception("No se pudo registrar el evento de fragmento")


def _window_start(days: int) -> datetime:
    """Devuelve el inicio de la ventana de análisis."""
    return timezone.now() - timedelta(days=days)


def snippet_error_rate(
    days: int = DEFAULT_WINDOW_DAYS,
    since: datetime | None = None,
) -> float | None:
    """Porcentaje de peticiones con status >= 400; ``None`` si no hay datos."""
    window_start = since if since is not None else _window_start(days)
    totals = SnippetRequest.objects.filter(created_at__gte=window_start).aggregate(
        total=Count("id"),
        errors=Count("id", filter=Q(status_code__gte=400)),
    )
    if not totals["total"]:
        return None
    return round(totals["errors"] / totals["total"] * 100, 2)


def tests_per_active_user_per_week(
    days: int = DEFAULT_WINDOW_DAYS,
    since: datetime | None = None,
) -> float | None:
    """Media de tests por usuario activo y semana; ``None`` sin datos."""
    window_start = since if since is not None else _window_start(days)
    results = TypingTestResult.objects.filter(date__gte=window_start)
    active_users = results.values("user").distinct().count()
    weeks = days / 7
    if not active_users or weeks <= 0:
        return None
    return round(results.count() / active_users / weeks, 2)


def share_of_users_with_results() -> float | None:
    """Porcentaje de usuarios no-staff con al menos un resultado."""
    users = get_user_model().objects.filter(is_staff=False)
    registered = users.count()
    if not registered:
        return None
    with_results = users.filter(typingtestresult__isnull=False).distinct().count()
    return round(with_results / registered * 100, 2)


def build_report(days: int = DEFAULT_WINDOW_DAYS) -> dict[str, float | int | None]:
    """Reúne las métricas de la ventana indicada con un único inicio."""
    since = _window_start(days)
    events = SnippetRequest.objects.filter(created_at__gte=since).count()
    return {
        "days": days,
        "events": events,
        "error_rate": snippet_error_rate(days, since),
        "tests_per_user_week": tests_per_active_user_per_week(days, since),
        "share_with_results": share_of_users_with_results(),
    }


def purge_snippet_requests(days: int = DEFAULT_RETENTION_DAYS) -> int:
    """Elimina los eventos más antiguos que la retención y devuelve el total."""
    if days < 1:
        raise ValueError("La retención debe ser de al menos un día")
    deleted, _ = SnippetRequest.objects.filter(created_at__lt=_window_start(days)).delete()
    return deleted


def maybe_purge_snippet_requests(days: int = DEFAULT_RETENTION_DAYS) -> int:
    """Ejecuta la purga como máximo una vez al día."""
    today = timezone.localdate().isoformat()
    if not cache.add(PURGE_CACHE_KEY, today, timeout=PURGE_CACHE_TIMEOUT):
        return 0
    return purge_snippet_requests(days)
