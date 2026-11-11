"""Vista del servicio de fragmentos de código."""

from __future__ import annotations

import time

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from .analytics import record_snippet_request
from .snippets import pick_snippet
from .validators import InvalidPayload, parse_language, read_json


@require_http_methods(["GET", "POST"])
def get_python_function(request: HttpRequest) -> JsonResponse:
    """Devuelve un fragmento de código aleatorio del lenguaje solicitado."""
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
