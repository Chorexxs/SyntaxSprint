"""Vista del servicio de fragmentos de código."""

from __future__ import annotations

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from .snippets import pick_snippet
from .validators import InvalidPayload, parse_language, read_json


@require_http_methods(["GET", "POST"])
def get_python_function(request: HttpRequest) -> JsonResponse:
    """Devuelve un fragmento de código aleatorio del lenguaje solicitado."""
    language = "python"
    if request.method == "POST":
        try:
            language = parse_language(read_json(request))
        except InvalidPayload as error:
            return JsonResponse({"error": str(error)}, status=400)

    return JsonResponse(pick_snippet(language))
