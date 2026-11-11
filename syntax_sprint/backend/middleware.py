"""Cabeceras de seguridad adicionales a las de Django."""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

# `unsafe-inline` es necesario para el script de tema que evita el FOUC y para el
# Tailwind Play CDN, que inyecta estilos y configuración en línea. Se puede endurecer
# con hashes/nonces cuando Tailwind se compile localmente (T007).
CSP_DIRECTIVES = (
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data:",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
)

CSP_POLICY = "; ".join(CSP_DIRECTIVES)


class ContentSecurityPolicyMiddleware:
    """Añade `Content-Security-Policy` a todas las respuestas."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response.headers.setdefault("Content-Security-Policy", CSP_POLICY)
        return response
