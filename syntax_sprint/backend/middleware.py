"""Cabeceras de seguridad adicionales a las de Django."""

from __future__ import annotations

from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import AdminTOTP
from .ratelimit import (ADMIN_LOGIN_LIMIT, ADMIN_LOGIN_PATH,
                        ADMIN_LOGIN_WINDOW_SECONDS, is_rate_limited,
                        reset_rate_limit)
from .two_factor import SESSION_KEY as ADMIN_TOTP_SESSION_KEY
from .two_factor import VERSION_KEY as ADMIN_TOTP_VERSION_KEY

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


ADMIN_TOTP_PREFIX = "/admin/"
ADMIN_TOTP_EXEMPT_PREFIXES = (
    "/admin/login/",
    "/admin/logout/",
    "/admin/2fa/",
    "/admin/jsi18n/",
)


class AdminTOTPMiddleware:
    """Exige el código TOTP al staff cuando la función está activada."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not settings.ADMIN_TOTP_REQUIRED:
            return self.get_response(request)

        path = request.path
        if not path.startswith(ADMIN_TOTP_PREFIX) or path.startswith(
            ADMIN_TOTP_EXEMPT_PREFIXES
        ):
            return self.get_response(request)

        user = request.user
        if not (user.is_authenticated and user.is_staff):
            return self.get_response(request)

        version = (
            AdminTOTP.objects.filter(user=user, confirmed=True)
            .values_list("version", flat=True)
            .first()
        )
        if (
            version is None
            or not request.session.get(ADMIN_TOTP_SESSION_KEY)
            or request.session.get(ADMIN_TOTP_VERSION_KEY) != version
        ):
            request.session.pop(ADMIN_TOTP_SESSION_KEY, None)
            request.session.pop(ADMIN_TOTP_VERSION_KEY, None)
            return redirect("admin_2fa")
        return self.get_response(request)


class AdminLoginRateLimitMiddleware:
    """Limita los intentos de login del admin por IP."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method != "POST" or request.path != ADMIN_LOGIN_PATH:
            return self.get_response(request)

        if is_rate_limited(
            request,
            "admin-login",
            ADMIN_LOGIN_LIMIT,
            ADMIN_LOGIN_WINDOW_SECONDS,
        ):
            return HttpResponse(
                "Demasiados intentos. Inténtalo de nuevo más tarde.",
                status=429,
                content_type="text/plain; charset=utf-8",
            )

        response = self.get_response(request)
        if response.status_code == 302 and not response.url.startswith(ADMIN_LOGIN_PATH):
            reset_rate_limit(request, "admin-login")
        return response
