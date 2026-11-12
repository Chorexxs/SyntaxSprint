"""Vista del servicio de fragmentos de código."""

from __future__ import annotations

import time

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from .analytics import record_snippet_request
from .ratelimit import SNIPPET_LIMIT, SNIPPET_WINDOW_SECONDS, is_rate_limited
from .snippets import pick_snippet
from .validators import InvalidPayload, parse_language, read_json


@require_http_methods(["GET", "POST"])
def get_python_function(request: HttpRequest) -> JsonResponse:
    """Devuelve un fragmento de código aleatorio del lenguaje solicitado."""
    if is_rate_limited(
        request,
        "snippet",
        SNIPPET_LIMIT,
        SNIPPET_WINDOW_SECONDS,
        alias=settings.SNIPPET_RATE_LIMIT_CACHE_ALIAS,
    ):
        return JsonResponse({"error": "Demasiadas peticiones"}, status=429)

    started = time.monotonic()
    language = "python"
    if request.method == "POST":
        try:
            language = parse_language(read_json(request))
        except InvalidPayload as error:
            record_snippet_request("unknown", 400, started)
            return JsonResponse({"error": str(error)}, status=400)

    response = JsonResponse(pick_snippet(language))
    record_snippet_request(language, response.status_code, started)
    return response
