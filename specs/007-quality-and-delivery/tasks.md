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

## Fase 6 — Render y estáticos

- [x] **T007-17** Añadir WhiteNoise y configurar `STORAGES` para servir estáticos con `DEBUG=False`.
  - Requisito: `RF-007-10`
  - Archivos: `settings.py`, `requirements.txt`, `.gitignore`
  - Evidencia: `collectstatic` copia 130 archivos y `findstatic` encuentra el CSS.

- [x] **T007-18** Detectar `RENDER_EXTERNAL_HOSTNAME` y permitir `DB_PATH` y `DATABASE_URL`.
  - Requisito: `RF-007-07`
  - Archivos: `settings.py`, `.env.example`
  - DoD: Render añade su host a `ALLOWED_HOSTS`/CSRF; PostgreSQL se activa con `DATABASE_URL`.

- [x] **T007-19** Crear `render.yaml` y `DEPLOY.md` con variables, build/start, backup y rotación.
  - Requisito: `RF-007-07`
  - DoD: el blueprint usa PostgreSQL free y el README enlaza la guía.

- [x] **T007-20** Verificar `collectstatic`, `check --deploy` y tests con los cambios de Render.
  - Requisito: `RF-007-10`
  - Evidencia: 130 estáticos, `check --deploy` con `DEBUG=False` → 0 issues, 26 tests OK.
  - DoD: 0 issues, 26 tests y estáticos encontrados.

- [x] **T007-21** Aplicar la configuración en Render, rotar `SECRET_KEY` y verificar la URL.
  - Requisito: `RF-007-07`
  - Evidencia: live en `https://syntaxsprint.onrender.com` (commit `eae7d68`); `/` 200,
    `/login` 200, `/static/css/styles.css` 200, `/admin/` 302; HSTS y cookies `Secure`.
  - Nota: sigue usando SQLite efímero; PostgreSQL queda en T007-22.
  - DoD: `/`, `/login`, `/static/css/styles.css` y `/admin/` responden; logs sin 500.

- [ ] **T007-22** Crear Render PostgreSQL y configurar `DATABASE_URL` para persistencia.
  - Requisito: `RF-007-07`
  - DoD: la base sobrevive a un redeploy y `migrate`/`loaddata` funcionan.

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
