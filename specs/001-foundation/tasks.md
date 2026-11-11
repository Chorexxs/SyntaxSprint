# Tareas 001 — Fundación del proyecto

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/001-foundation/spec.md`

## Fase 1 — Base existente

- [x] **T001-01** Configurar `python-decouple` para `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS`.
  - Requisito: `RF-001-01`
  - Archivos: `syntax_sprint/syntax_sprint/settings.py`
  - DoD: el servidor arranca leyendo `.env`.

- [x] **T001-02** Registrar la app `backend` y configurar SQLite en `BASE_DIR/db.sqlite3`.
  - Requisitos: `RF-001-02`, `RF-001-07`
  - Archivos: `settings.py`, `backend/apps.py`

- [x] **T001-03** Conectar plantillas y estáticos del proyecto.
  - Requisitos: `RF-001-03`, `RF-001-04`
  - Archivos: `settings.py`
  - DoD: `/` renderiza y carga `styles.css` y `script.js`.

## Fase 2 — Limpieza

- [x] **T001-04** Eliminar la ruta heredada `BASE_DIR.parent/templates` de `TEMPLATES[0]["DIRS"]`.
  - Requisito: `RF-001-03`
  - Archivos: `settings.py`
  - DoD: `manage.py check` OK y no existen referencias a plantillas externas.
  - Evidencia: `settings.py:82` queda en `[BASE_DIR / "templates"]`; no hay ninguna
    carpeta `templates/` en la raíz del repositorio y `manage.py check` + los 31 tests
    siguen en verde.

- [x] **T001-05** Alinear la versión de Django entre `requirements.txt`, `README.md` y la migración.
  - Requisito: `RF-001-08`
  - Archivos: `requirements.txt`, `README.md`
  - DoD: una sola versión documentada y reproducible en entorno limpio.
  - Evidencia: `requirements.txt` y `README.md:24` declaran Django 5.2.17.

- [x] **T001-06** Crear `.env.example` con las tres variables y sin valores reales.
  - Requisito: `RF-001-01`, `RNF-001-03`
  - Archivos: `.env.example`
  - DoD: un desarrollador nuevo puede configurar el proyecto siguiéndolo.
  - Evidencia: `.env.example` versionado con `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`,
    `CSRF_TRUSTED_ORIGINS`, `TRUST_PROXY_HEADERS`, `DATABASE_URL` y `DB_PATH` sin
    valores reales.

- [x] **T001-07** Parsear `ALLOWED_HOSTS` ignorando cadenas vacías.
  - Requisito: `RF-001-01`
  - Archivos: `settings.py`
  - DoD: `ALLOWED_HOSTS=""` produce `[]` y no un host vacío.
  - Evidencia: `_csv_env` (`settings.py:23-26`) descarta entradas vacías; cubierto
    además por `T009-25`.

## Fase 3 — Admin y limpieza de código

- [x] **T001-08** Registrar `TypingTestResult` en el admin con listado y filtros.
  - Requisito: `RF-001-06`
  - Archivos: `backend/admin.py`
  - DoD: `/admin/` muestra el modelo y filtra por fecha y usuario.
  - Evidencia: `TypingTestResultAdmin` con `list_display`, `list_filter`,
    `search_fields`, `ordering` y `date_hierarchy`.

- [x] **T001-09** Eliminar imports duplicados y sin usar en `views.py` (`HttpResponse`, `requests`, bloque repetido).
  - Requisito: `RNF-001-02`
  - Archivos: `backend/views.py`
  - DoD: `pylint` no reporta `unused-import` ni `duplicate-code` en ese archivo.
  - Evidencia: no hay duplicados; `pylint` con `--enable=unused-import,ungrouped-imports`
    no reporta avisos en `backend/`.

## Fase 4 — Verificación

- [x] **T001-10** Ejecutar `python manage.py check` y adjuntar salida en la PR.
  - Requisito: `RNF-001-01`
  - Evidencia: `manage.py check` → `System check identified no issues (0 silenced)`.

## Deuda técnica / Backlog

- [ ] Añadir `.env.test` o fixtures para tests reproducibles.
- [ ] Documentar rotación de `SECRET_KEY`.
- [ ] Evaluar `whitenoise` para servir estáticos sin servidor web (ver 007).

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Creación a partir del estado real del repositorio |
| 2026-11-11 | T001-04 cerrada: `TEMPLATES[0]["DIRS"]` solo apunta a `BASE_DIR/templates` |
