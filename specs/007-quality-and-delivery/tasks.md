# Tareas 007 — Calidad, seguridad y despliegue

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/007-quality-and-delivery/spec.md`

## Fase 1 — Red de seguridad (prioridad máxima)

- [x] **T007-01** Crear `AuthTests` con 6 casos (registro, duplicados, login, logout, anónimo).
  - Requisitos: `RF-007-01`, `RF-007-02`
  - Archivos: `backend/tests.py`
  - DoD: `manage.py test backend.tests.AuthTests` en verde.
  - Evidencia: 12 casos (registro, campos vacíos, contraseñas, contraseña débil,
    duplicado, login válido/erróneo, rate limit, logout POST, rutas protegidas).
    Supera los 6 casos previstos.

- [x] **T007-02** Crear `SnippetTests` con 4 casos (válido, fallback, GET, JSON inválido).
  - Requisito: `RF-007-04`
  - Archivos: `backend/tests.py`
  - Evidencia: 5 casos en verde, incluido `405` para `PUT`.

- [x] **T007-03** Crear `ResultTests` con 5 casos (login, válido, inválido, método, rangos).
  - Requisitos: `RF-007-01`, `RF-007-04`, `RF-007-06`
  - Archivos: `backend/tests.py`
  - Evidencia: 6 casos en verde (válido, JSON inválido, claves ausentes, rangos,
    `GET` → 405, aislamiento entre usuarios).

- [x] **T007-04** Crear `ProfileTests` con 4 casos (login, aislamiento, promedios, vacío).
  - Requisitos: `RF-007-01`
  - Archivos: `backend/tests.py`
  - Evidencia: `ProfileTests.test_requires_login`, `test_isolation_between_users`,
    `test_averages` (60/90 + 80/100 → 70/95) y `test_empty_state` (0/0 y "no results
    yet"). Los dos primeros se movieron desde `AuthTests` y `ResultTests` para no
    duplicarlos. Suite total: 30 tests.

- [x] **T007-05** Alcanzar ≥ 80 % de cobertura en `backend/` y documentar el comando.
  - Requisito: `RNF-007-02`
  - DoD: `coverage report` muestra el porcentaje en la PR.
  - Evidencia: `coverage run --source=backend manage.py test` + `coverage report` →
    98 % total; `views.py` 96 % y `models.py` 89 %.

## Fase 2 — Correcciones habilitadas por los tests

- [x] **T007-06** Añadir `{% csrf_token %}` en `index.html` (depende de T004-08).
  - Requisito: `RF-007-09`
  - Evidencia: `index.html:44`; test `test_index_sets_csrf_cookie`.

- [x] **T007-07** Asegurar 400 ante JSON inválido en ambos endpoints (depende de T003-06 y T005-05).
  - Requisito: `RF-007-04`
  - Evidencia: tests `SnippetTests.test_invalid_json_returns_400` y
    `ResultTests.test_save_invalid_json`.

## Fase 3 — Seguridad de producción

- [x] **T007-08** Añadir bloque `if not DEBUG` con HTTPS, cookies seguras y HSTS.
  - Requisito: `RF-007-05`
  - Archivos: `settings.py`
  - DoD: `check --deploy` sin warnings críticos.
  - Evidencia: `settings.py:179-193` (SSL redirect, cookies `Secure`, HSTS,
    `nosniff`, Referrer-Policy, `X_FRAME_OPTIONS`).

- [x] **T007-09** Configurar servicio de estáticos (`whitenoise` o servidor web) y validar `collectstatic`.
  - Requisito: `RF-007-10`
  - DoD: `staticfiles/css/styles.css` existe y se sirve con `DEBUG=False`.
  - Evidencia: `T007-17` (WhiteNoise + `STORAGES`) y `T007-20` (130 estáticos).

- [x] **T007-10** Documentar el despliegue con Gunicorn y el checklist del `plan.md`.
  - Requisito: `RF-007-07`
  - Archivos: `README.md`
  - Evidencia: `DEPLOY.md`, `render.yaml` y `gunicorn.conf.py`; enlazados desde el
    README.

## Fase 4 — Automatización

- [x] **T007-11** Crear `.github/workflows/ci.yml` con lint, check, migraciones y tests.
  - Requisitos: `RF-007-11`, `RF-007-03`
  - DoD: el workflow pasa en `main` y falla ante un test roto.
  - Evidencia: `.github/workflows/ci.yml` en push/PR a `main` con
    `isort --check-only --diff .`, `manage.py check`, `makemigrations --check --dry-run`,
    `manage.py test`, `pylint` bloqueante con `.pylintrc`, `code_metrics.py --strict` y
    la comprobación del CSS compilado (`T008-16`). Los pasos se replicaron en local con
    el mismo entorno y terminaron con código 0.

- [x] **T007-12** Añadir `coverage` (y opcionalmente `pytest-django`) a `requirements.txt`.
  - Requisito: `RNF-007-02`
  - Evidencia: `coverage==7.17.2` en `requirements-dev.txt` (no en producción).

- [x] **T007-13** Ejecutar `isort` y `pylint` y registrar la línea base de avisos.
  - Requisito: `RF-007-03`
  - DoD: deuda restante listada por archivo, sin errores nuevos.
  - Evidencia: `isort --check-only --diff .` sin avisos. `pylint backend
    --rcfile=../.pylintrc` (con `pylint-django`) → **10.00/10** y 0 mensajes; se añadió
    `.pylintrc` y docstrings de módulo en `admin`, `apps`, `models` y `urls`.

## Fase 5 — Documentación

- [x] **T007-14** Corregir el árbol de directorios del README y la versión de Django.
  - Requisito: `RF-007-08`
  - Archivos: `README.md`
  - Evidencia: `README.md:24` declara Django 5.2.17 y el árbol refleja
    `syntax_sprint/`.

- [x] **T007-15** Actualizar `specs/traceability.md` con el estado final.
  - Requisito: `RF-007-08`
  - Evidencia: matriz revisada contra código y tests (`26 tests OK`, `check` 0 issues,
    `isort` limpio). Estados `?`/`??` sustituidos por ✅/🟡/⬜ con notas.

- [x] **T007-16** Decidir si `AGENTS.md` debe versionarse (hoy está en `.gitignore`).
  - Requisito: `RF-007-08`
  - DoD: decisión documentada en `plan.md` o en el README.
  - Evidencia: `AGENTS.md` está versionado (`git ls-files AGENTS.md`) y ya no figura
    en `.gitignore`. Decisión: se versiona como fuente de convenciones.

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

- [x] **T007-22** Conectar InsForge PostgreSQL y configurar `DATABASE_URL`.
  - Requisito: `RF-007-07`
  - Evidencia: 11 tablas Django en InsForge; signup de prueba en producción visible
    en `auth_user`; `/` 200.
  - Nota: requiere CLI >= 0.2.8 (`npx -y @insforge/cli@latest db connection-string`).
  - DoD: la base sobrevive a un redeploy y `migrate`/`loaddata` funcionan.

## Deuda técnica / Backlog

- [ ] Pre-commit hooks (`isort`, `pylint`, `django check`).
- [ ] Dependabot para actualizaciones de seguridad.
- [ ] Migrar a PostgreSQL si aumenta la concurrencia.
- [ ] Dockerfile de producción.
- [ ] Sentry o logging estructurado.
- [ ] Tests E2E con Playwright del flujo completo.
- [x] Compilar Tailwind y eliminar el CDN.
  - Evidencia: build local con `npm run build:css` (Tailwind 3.4.17) y
    `static/css/tailwind.css` versionado; `base.html` ya no usa el CDN.
  - Fecha: 2026-11-11.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Plan inicial; suite de tests vacía detectada |
| 2026-11-10 | Verificación contra código: 26 tests en verde, `check` 0 issues, `isort` limpio; `T007-01`…`T007-03`, `T007-06`…`T007-10` y `T007-14`…`T007-16` cerradas |
| 2026-11-10 | CI en GitHub Actions con isort, check, migraciones y tests (`T007-11`) |
