# Tareas 011 — Analítica de producto

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/011-analytics/spec.md`

## Fase 1 — Base

- [x] **T011-01** Crear el modelo `SnippetRequest` y su migración.
  - Requisito: `RF-011-01`, `RF-011-07`
  - Archivos: `backend/models.py`, `backend/migrations/0002_snippetrequest.py`
  - Evidencia: `makemigrations --check --dry-run` sin cambios pendientes; campos sin IP,
    user-agent, email ni FK a usuario.

- [x] **T011-02** Implementar `record_snippet_request` y las agregaciones en `analytics.py`.
  - Requisitos: `RF-011-01`, `RF-011-02`, `RF-011-06`
  - Archivos: `backend/analytics.py`
  - Evidencia: captura `DatabaseError`, registra con `logger.exception` y las funciones
    devuelven `None` cuando no hay datos.

## Fase 2 — Implementación

- [x] **T011-03** Instrumentar `get_python_function` sin alterar su contrato.
  - Requisitos: `RF-011-01`, `RF-011-02`
  - Archivos: `backend/snippet_views.py`
  - Evidencia: sigue devolviendo `{name, code}` y 400 ante JSON inválido; el evento
    guarda duración, estado y lenguaje solicitado (recortado a 32).

- [x] **T011-04** Añadir los comandos `analytics_report` y `purge_analytics`.
  - Requisitos: `RF-011-03`, `RF-011-04`, `RF-011-06`
  - Archivos: `backend/management/commands/analytics_report.py`, `purge_analytics.py`
  - Evidencia: con una BD temporal, `analytics_report` imprime
    "sin datos en la ventana" y sale con 0; `purge_analytics --days 90` responde
    "0 eventos eliminados".

- [x] **T011-05** Registrar el modelo en el admin en solo lectura.
  - Requisito: `RF-011-05`
  - Archivos: `backend/admin.py`
  - Evidencia: `has_add_permission`, `has_change_permission` y `has_delete_permission`
    devuelven `False`; listado con filtros por estado y lenguaje.

- [x] **T011-06** Escribir `AnalyticsTests` con los criterios de aceptación.
  - Requisitos: `CA-011-01`…`CA-011-10`
  - Archivos: `backend/tests.py`
  - Evidencia: 10 casos nuevos; `manage.py test` → **52 tests OK**.

## Fase 3 — Verificación

- [x] **T011-07** Ejecutar la verificación y actualizar la trazabilidad.
  - Requisitos: `RNF-011-01`…`RNF-011-05`
  - Evidencia: `manage.py check` 0 issues; `manage.py test` 52 OK; cobertura 99 %
    (651 sentencias, 6 sin cubrir); `isort` sin avisos; `pylint` 10.00/10;
    `code_metrics.py --strict` sin incumplimientos; `check_dependencies.py --strict` OK.
    `specs/traceability.md`, `specs/000-overview/spec.md` y `plan.md` actualizados.

- [x] **T011-08** Purga oportunista diaria y validación de ventanas.
  - Requisitos: `RF-011-04`, `RF-011-08`
  - Archivos: `backend/analytics.py`, `backend/management/commands/`
  - Evidencia: `maybe_purge_snippet_requests` usa `cache.add` con clave diaria;
    `purge_analytics --days 0` y `analytics_report --days -1` lanzan `CommandError`.
    Tests `test_opportunistic_purge_runs_once_per_day` y
    `test_purge_commands_reject_non_positive_days` (SEC-018/SEC-019).

## Deuda técnica / Backlog

- [ ] Panel de métricas en `/admin/` con series temporales.
- [ ] Alertas cuando una métrica incumple su objetivo.
- [ ] Medir también los resultados anónimos (requiere un identificador de sesión).
- [ ] Exportar el informe a CSV o JSON para históricos.

## Historial

| Fecha | Cambio | Autor |
| --- | --- | --- |
| 2026-11-11 | Creación de la spec, el plan y las tareas | Agente |
| 2026-11-11 | Implementación completa y verificación en verde |
| 2026-11-11 | Endurecimiento tras auditoría: purga diaria, validación de días y rate limit (T011-08, T003-11) | Agente |
