# Plan técnico 003 — Servicio de fragmentos de código

| Campo | Valor |
| --- | --- |
| Spec | `specs/003-snippet-service/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Extraer el diccionario `code_snippets` a `backend/snippets.py` como constante de módulo,
añadir un helper `pick_snippet(language)` y dejar la vista como orquestador HTTP.
Mantener la ruta y el contrato actuales para no romper el frontend.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `backend/snippets.py` | Crear | Catálogo `CODE_SNIPPETS` + `SUPPORTED_LANGUAGES` + `pick_snippet`. |
| `backend/views.py` | Modificar | Vista delgada, manejo de JSON inválido. |
| `backend/tests.py` | Añadir | Tests de contrato y aleatoriedad. |

## 3. Diseño de datos

```python
# backend/snippets.py
SUPPORTED_LANGUAGES = ("python", "javascript", "typescript", "html", "css", "sql", "java", "go")

CODE_SNIPPETS: dict[str, list[dict[str, str]]] = {
    "python": [{"name": "Hello World", "code": "print(\"Hello, World!\")"}, ...],
    ...
}

def pick_snippet(language: str | None) -> dict[str, str]:
    return random.choice(CODE_SNIPPETS.get(language or "python", CODE_SNIPPETS["python"]))
```

Sin migraciones.

## 4. Contrato y flujo

```text
POST /get_python_function
  body = json.loads(request.body or b"{}")     # try/except → 400
  language = body.get("language", "python")
  snippet = pick_snippet(language)             # fallback python
  return JsonResponse(snippet)                 # 200
```

Respuesta de error:

```json
{ "error": "Cuerpo JSON inválido" }
```

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| Mantener catálogo en `views.py` | Cero cambios | Archivo de 282 líneas y creciendo | No |
| Guardar fragmentos en BD | Editable desde admin | Migración, fixtures y consultas | No |
| Cargar JSON estático en `static/` | Sin backend | Sin control de idioma y sin CSRF | No |
| Cambiar endpoint a `/api/snippets/random` | Semántica clara | Rompe contrato | No (backlog con alias) |

## 6. Estrategia de pruebas

| Caso | Entrada | Esperado |
| --- | --- | --- |
| Lenguaje válido | `{"language": "css"}` | 200, `name` y `code` presentes |
| Lenguaje desconocido | `{"language": "cobol"}` | 200, fragmento Python |
| GET | — | 200, fragmento Python |
| JSON inválido | `b"{"` | 400, `error` |
| Catálogo completo | — | 8 claves, ≥15 por clave, sin duplicados internos |
| Aleatoriedad | 20 POST python | ≥3 `name` distintos |

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Tests de aleatoriedad inestables | Media | Usar `random.seed` o comprobar pertenencia, no valor exacto |
| Duplicar el catálogo por error | Baja | Una sola fuente de verdad |
| Código con caracteres no ASCII | Baja | Test de longitud y `encode("utf-8")` |

## 8. Orden de implementación

1. Crear `snippets.py` moviendo el diccionario tal cual.
2. Refactorizar la vista y manejar `json.JSONDecodeError`.
3. Tests de contrato.
4. Validar que el frontend sigue funcionando.

## 9. Notas de despliegue

- Sin migraciones ni variables nuevas.
- Sin cambios en el HTML.
