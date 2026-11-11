"""Cabeceras de seguridad adicionales a las de Django."""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

# Sin `unsafe-inline`: el tema se inicializa con un script externo y Tailwind está
# compilado localmente, así que no hay scripts ni estilos en línea.
CSP_DIRECTIVES = (
    "default-src 'self'",
    "script-src 'self'",
    "style-src 'self' https://fonts.googleapis.com",
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
