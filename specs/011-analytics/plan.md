# Plan técnico 011 — Analítica de producto

| Campo | Valor |
| --- | --- |
| Spec | `specs/011-analytics/spec.md` |
| Estado | Aprobado |
| Autor | Agente |
| Última revisión | 2026-11-11 |

## 1. Enfoque

Se añade un modelo propio, `SnippetRequest`, que guarda una fila por petición al endpoint de
fragmentos con lenguaje, código HTTP, duración y fecha. La vista instrumenta la llamada con
un `try/except` que nunca rompe la respuesta. Un módulo `analytics.py` concentra el registro
y las agregaciones; dos comandos de gestión (informe y purga) y el admin completan la
funcionalidad. No se añaden dependencias ni scripts de terceros: todo vive en PostgreSQL y
en el admin que ya existe.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `backend/models.py` | Modificar | Añadir `SnippetRequest` y su `__str__`. |
| `backend/migrations/0002_snippetrequest.py` | Añadir | Migración aditiva y reversible. |
| `backend/analytics.py` | Añadir | `record_snippet_request()` y funciones de métricas. |
| `backend/snippet_views.py` | Modificar | Medir duración y registrar el resultado. |
| `backend/management/commands/analytics_report.py` | Añadir | Informe de métricas por ventana. |
| `backend/management/commands/purge_analytics.py` | Añadir | Purga por retención. |
| `backend/admin.py` | Modificar | Registrar `SnippetRequest` en solo lectura. |
| `backend/tests.py` | Añadir | `AnalyticsTests` con registro, fallo y matemática. |

## 3. Diseño de datos

```text
SnippetRequest
├── created_at: DateTimeField(auto_now_add, db_index)
├── language: CharField(32)
├── status_code: PositiveSmallIntegerField(db_index)
└── duration_ms: PositiveIntegerField
```

Migración necesaria: sí (`0002_snippetrequest`). Reversible: sí (`DeleteModel`).

## 4. Contratos y flujos

```text
Cliente → POST /get_python_function
  → vista: mide t0 → valida payload → pick_snippet
  → analytics.record_snippet_request(language, status, t0)
       └─ INSERT en SnippetRequest (fail-open)
  → JsonResponse
```

Registro (pseudocódigo):

```python
def record_snippet_request(language, status_code, started):
    try:
        SnippetRequest.objects.create(
            language=language or "unknown",
            status_code=status_code,
            duration_ms=max(int((time.monotonic() - started) * 1000), 0),
        )
    except DatabaseError:  # la analítica nunca rompe el endpoint
        logger.exception("No se pudo registrar el evento de fragmento")
```

Informe:

```text
== Analítica (últimos 28 días) ==
Tests por usuario activo y semana ... 2.50  (objetivo >= 3)
Error rate de /get_python_function . 0.80 % (objetivo < 1 %)
Usuarios con al menos un resultado . 62.50 % (objetivo >= 60 %)
Eventos de fragmentos ............. 1200
Lighthouse: mide con `lighthouse https://syntaxsprint.onrender.com/`
```

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| Modelo propio en PostgreSQL | Sin dependencias ni cookies; consultable con Django | Hay que escribir el modelo y los comandos | Sí |
| Plausible/Umami autoalojado | Panel listo | Servicio extra, coste y consentimiento | No |
| PostHog/GA4 | Embudos y retención | Cookies de terceros, consentimiento y transferencia de datos | No |
| Solo `logging` | Cero esquema | No agregable; depende del proveedor de logs | No |
| `django-axes`/middleware genérico | Reutilizable | Mide otra cosa y añade dependencia | No |

## 6. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Integración | POST válido e inválido crean el evento correcto | `Client` + `TestCase` |
| Unitario | `record_snippet_request` no propaga errores | `mock.patch` |
| Unitario | Error rate, tests/usuario/semana y porcentaje | `TestCase` con datos fijos |
| Integración | `analytics_report` sin datos devuelve "sin datos" y código 0 | `call_command` |
| Integración | `purge_analytics` respeta la retención | `call_command` |
| Integración | El admin no permite añadir ni editar | `admin.site` |

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| La inserción ralentiza el endpoint | Baja | Una sola escritura; duración registrada para vigilarlo. |
| División por cero en el informe | Media | Funciones devuelven `None`/"sin datos" sin datos. |
| Zona horaria en las ventanas | Media | `timezone.now()` y `USE_TZ=True`. |
| Migración en Render | Baja | Aditiva, reversible y aplicada por el `startCommand`. |

## 8. Orden de implementación

1. Modelo `SnippetRequest` y migración.
2. `analytics.py` con registro y agregaciones.
3. Instrumentar `snippet_views.get_python_function`.
4. Comandos `analytics_report` y `purge_analytics`.
5. Admin en solo lectura.
6. Pruebas y verificación (`check`, `test`, `isort`, `pylint`).
7. Trazabilidad y documentación.

## 9. Notas de despliegue

- Migraciones: `0002_snippetrequest` se aplica con `manage.py migrate` en el arranque.
- Variables de entorno: ninguna nueva.
- Estáticos: sin cambios.
- Sin cookies ni scripts de terceros: la CSP actual no se toca.
