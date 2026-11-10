# Tareas 007 — Calidad, seguridad y despliegue

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/007-quality-and-delivery/spec.md`

## Fase 1 — Red de seguridad (prioridad máxima)

- [ ] **T007-01** Crear `AuthTests` con 6 casos (registro, duplicados, login, logout, anónimo).
  - Requisitos: `RF-007-01`, `RF-007-02`
  - Archivos: `backend/tests.py`
  - DoD: `manage.py test backend.tests.AuthTests` en verde.

- [ ] **T007-02** Crear `SnippetTests` con 4 casos (válido, fallback, GET, JSON inválido).
  - Requisito: `RF-007-04`
  - Archivos: `backend/tests.py`

- [ ] **T007-03** Crear `ResultTests` con 5 casos (login, válido, inválido, método, rangos).
  - Requisitos: `RF-007-01`, `RF-007-04`, `RF-007-06`
  - Archivos: `backend/tests.py`

- [ ] **T007-04** Crear `ProfileTests` con 4 casos (login, aislamiento, promedios, vacío).
  - Requisitos: `RF-007-01`
  - Archivos: `backend/tests.py`

- [ ] **T007-05** Alcanzar ≥ 80 % de cobertura en `backend/` y documentar el comando.
  - Requisito: `RNF-007-02`
  - DoD: `coverage report` muestra el porcentaje en la PR.

## Fase 2 — Correcciones habilitadas por los tests

- [ ] **T007-06** Añadir `{% csrf_token %}` en `index.html` (depende de T004-08).
  - Requisito: `RF-007-09`

- [ ] **T007-07** Asegurar 400 ante JSON inválido en ambos endpoints (depende de T003-06 y T005-05).
  - Requisito: `RF-007-04`

## Fase 3 — Seguridad de producción

- [ ] **T007-08** Añadir bloque `if not DEBUG` con HTTPS, cookies seguras y HSTS.
  - Requisito: `RF-007-05`
  - Archivos: `settings.py`
  - DoD: `check --deploy` sin warnings críticos.

- [ ] **T007-09** Configurar servicio de estáticos (`whitenoise` o servidor web) y validar `collectstatic`.
  - Requisito: `RF-007-10`
  - DoD: `staticfiles/css/styles.css` existe y se sirve con `DEBUG=False`.

- [ ] **T007-10** Documentar el despliegue con Gunicorn y el checklist del `plan.md`.
  - Requisito: `RF-007-07`
  - Archivos: `README.md`

## Fase 4 — Automatización

- [ ] **T007-11** Crear `.github/workflows/ci.yml` con lint, check, migraciones y tests.
  - Requisitos: `RF-007-11`, `RF-007-03`
  - DoD: el workflow pasa en `main` y falla ante un test roto.

- [ ] **T007-12** Añadir `coverage` (y opcionalmente `pytest-django`) a `requirements.txt`.
  - Requisito: `RNF-007-02`

- [ ] **T007-13** Ejecutar `isort` y `pylint` y registrar la línea base de avisos.
  - Requisito: `RF-007-03`
  - DoD: deuda restante listada por archivo, sin errores nuevos.

## Fase 5 — Documentación

- [ ] **T007-14** Corregir el árbol de directorios del README y la versión de Django.
  - Requisito: `RF-007-08`
  - Archivos: `README.md`

- [ ] **T007-15** Actualizar `specs/traceability.md` con el estado final.
  - Requisito: `RF-007-08`

- [ ] **T007-16** Decidir si `AGENTS.md` debe versionarse (hoy está en `.gitignore`).
  - Requisito: `RF-007-08`
  - DoD: decisión documentada en `plan.md` o en el README.

## Deuda técnica / Backlog

- [ ] Pre-commit hooks (`isort`, `pylint`, `django check`).
- [ ] Dependabot para actualizaciones de seguridad.
- [ ] Migrar a PostgreSQL si aumenta la concurrencia.
- [ ] Dockerfile de producción.
- [ ] Sentry o logging estructurado.
- [ ] Tests E2E con Playwright del flujo completo.
- [ ] Compilar Tailwind y eliminar el CDN.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Plan inicial; suite de tests vacía detectada |
