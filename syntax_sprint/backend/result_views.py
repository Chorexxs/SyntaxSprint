"""Vistas de resultados y perfil del usuario."""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import TypingTestResult
from .validators import InvalidPayload, parse_result, read_json


@login_required(login_url="login")
@require_POST
def save_typing_test_result(request: HttpRequest) -> JsonResponse:
    """Guarda un resultado validando tipo y rango en el servidor."""
    try:
        wpm, accuracy = parse_result(read_json(request))
    except InvalidPayload as error:
        return JsonResponse({"error": str(error)}, status=400)

    TypingTestResult.objects.create(user=request.user, wpm=wpm, accuracy=accuracy)
    return JsonResponse({"message": "Resultado guardado exitosamente"})


@login_required(login_url="login")
def profile(request: HttpRequest) -> HttpResponse:
    """Muestra el historial paginado y los promedios del usuario autenticado."""
    results = TypingTestResult.objects.filter(user=request.user).order_by("-date")
    stats = results.aggregate(avg_wpm=Avg("wpm"), avg_accuracy=Avg("accuracy"))
    page_obj = Paginator(results, 20).get_page(request.GET.get("page"))

    context = {
        "results": page_obj,
        "page_obj": page_obj,
        "avg_wpm": stats["avg_wpm"] or 0,
        "avg_accuracy": stats["avg_accuracy"] or 0,
    }
    return render(request, "profile.html", context)
