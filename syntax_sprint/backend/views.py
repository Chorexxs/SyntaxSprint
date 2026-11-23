"""Vistas de las páginas públicas del proyecto."""

from __future__ import annotations

from django.db import DatabaseError, connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_safe


def index(request: HttpRequest) -> HttpResponse:
    """Renderiza la portada pública del test."""
    return render(request, "index.html")


def _database_ping() -> None:
    """Ejecuta una consulta mínima para comprobar que la base de datos responde."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()


@require_safe
def healthz(request: HttpRequest) -> JsonResponse:
    """Prueba de vida que toca la base de datos para generar actividad real."""
    try:
        _database_ping()
    except DatabaseError:
        return JsonResponse({"status": "error"}, status=503)

    response = JsonResponse({"status": "ok"})
    response["Cache-Control"] = "no-store"
    return response
