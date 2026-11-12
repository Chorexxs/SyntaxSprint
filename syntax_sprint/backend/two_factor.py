"""Verificación TOTP del admin (spec 012)."""

from __future__ import annotations

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import AdminTOTP
from .ratelimit import (ADMIN_2FA_LIMIT, ADMIN_2FA_WINDOW_SECONDS, client_ip,
                        is_rate_limited, reset_rate_limit)
from .totp import verify_code

logger = logging.getLogger(__name__)

SESSION_KEY = "admin_totp_ok"
VERSION_KEY = "admin_totp_version"
RATE_LIMIT_SCOPE = "admin-2fa"


@login_required(login_url="admin:login")
@require_http_methods(["GET", "POST"])
def admin_2fa(request: HttpRequest) -> HttpResponse:
    """Pide el código TOTP y marca la sesión como verificada."""
    if not request.user.is_staff:
        return redirect("index")

    device = AdminTOTP.objects.filter(user=request.user, confirmed=True).first()
    if device is None:
        return render(request, "admin_2fa_setup.html", status=403)

    if request.method == "POST":
        if is_rate_limited(
            request,
            RATE_LIMIT_SCOPE,
            ADMIN_2FA_LIMIT,
            ADMIN_2FA_WINDOW_SECONDS,
        ):
            logger.warning("Verificación 2FA bloqueada para %s", client_ip(request))
            return HttpResponse(
                "Demasiados intentos. Inténtalo de nuevo más tarde.",
                status=429,
                content_type="text/plain; charset=utf-8",
            )

        code = (request.POST.get("code") or "").strip()
        valid, counter = verify_code(device.secret, code, device.last_counter)
        if valid:
            reset_rate_limit(request, RATE_LIMIT_SCOPE)
            device.last_counter = counter
            device.save(update_fields=["last_counter"])
            request.session[SESSION_KEY] = True
            request.session[VERSION_KEY] = device.version
            request.session.cycle_key()
            return redirect("admin:index")
        messages.error(request, "Código incorrecto o ya utilizado.")

    return render(request, "admin_2fa.html")
