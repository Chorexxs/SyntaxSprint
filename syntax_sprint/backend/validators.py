"""Validación de las cargas JSON que reciben las vistas."""

from __future__ import annotations

import json
import math
from typing import Any

from django.http import HttpRequest

WPM_MAX = 400.0
ACCURACY_MAX = 100.0


class InvalidPayload(ValueError):
    """Los datos recibidos no son válidos."""


def read_json(request: HttpRequest) -> Any:
    """Devuelve el JSON del cuerpo o lanza ``InvalidPayload``."""
    try:
        return json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InvalidPayload("Cuerpo JSON inválido") from exc


def parse_language(payload: Any) -> str:
    """Extrae el lenguaje solicitado; si no es válido, usa Python."""
    if not isinstance(payload, dict):
        return "python"
    language = payload.get("language", "python")
    return language if isinstance(language, str) else "python"


def parse_result(payload: Any) -> tuple[float, float]:
    """Valida y devuelve ``(wpm, accuracy)`` o lanza ``InvalidPayload``."""
    if not isinstance(payload, dict):
        raise InvalidPayload("Datos no válidos")

    try:
        wpm = float(payload["wpm"])
        accuracy = float(payload["accuracy"])
    except (KeyError, TypeError, ValueError) as exc:
        raise InvalidPayload("Datos no válidos") from exc

    if not math.isfinite(wpm) or not 0 <= wpm <= WPM_MAX:
        raise InvalidPayload("WPM fuera de rango")
    if not math.isfinite(accuracy) or not 0 <= accuracy <= ACCURACY_MAX:
        raise InvalidPayload("Precisión fuera de rango")
    return wpm, accuracy
