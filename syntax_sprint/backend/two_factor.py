"""Verificación TOTP del admin (spec 012)."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .models import AdminTOTP
from .totp import verify_code

SESSION_KEY = "admin_totp_ok"


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
        code = (request.POST.get("code") or "").strip()
        valid, counter = verify_code(device.secret, code, device.last_counter)
        if valid:
            device.last_counter = counter
            device.save(update_fields=["last_counter"])
            request.session[SESSION_KEY] = True
            request.session.cycle_key()
            return redirect("admin:index")
        messages.error(request, "Código incorrecto o ya utilizado.")

    return render(request, "admin_2fa.html")
