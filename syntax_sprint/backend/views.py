"""Vistas de las páginas públicas del proyecto."""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Renderiza la portada pública del test."""
    return render(request, "index.html")
