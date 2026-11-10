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

- [ ] **T001-04** Eliminar la ruta heredada `BASE_DIR.parent/templates` de `TEMPLATES[0]["DIRS"]`.
  - Requisito: `RF-001-03`
  - Archivos: `settings.py`
  - DoD: `manage.py check` OK y no existen referencias a plantillas externas.

- [ ] **T001-05** Alinear la versión de Django entre `requirements.txt`, `README.md` y la migración.
  - Requisito: `RF-001-08`
  - Archivos: `requirements.txt`, `README.md`
  - DoD: una sola versión documentada y reproducible en entorno limpio.

- [ ] **T001-06** Crear `.env.example` con las tres variables y sin valores reales.
  - Requisito: `RF-001-01`, `RNF-001-03`
  - Archivos: `.env.example`
  - DoD: un desarrollador nuevo puede configurar el proyecto siguiéndolo.

- [ ] **T001-07** Parsear `ALLOWED_HOSTS` ignorando cadenas vacías.
  - Requisito: `RF-001-01`
  - Archivos: `settings.py`
  - DoD: `ALLOWED_HOSTS=""` produce `[]` y no un host vacío.

## Fase 3 — Admin y limpieza de código

- [ ] **T001-08** Registrar `TypingTestResult` en el admin con listado y filtros.
  - Requisito: `RF-001-06`
  - Archivos: `backend/admin.py`
  - DoD: `/admin/` muestra el modelo y filtra por fecha y usuario.

- [ ] **T001-09** Eliminar imports duplicados y sin usar en `views.py` (`HttpResponse`, `requests`, bloque repetido).
  - Requisito: `RNF-001-02`
  - Archivos: `backend/views.py`
  - DoD: `pylint` no reporta `unused-import` ni `duplicate-code` en ese archivo.

## Fase 4 — Verificación

- [ ] **T001-10** Ejecutar `python manage.py check` y adjuntar salida en la PR.
  - Requisito: `RNF-001-01`

## Deuda técnica / Backlog

- [ ] Añadir `.env.test` o fixtures para tests reproducibles.
- [ ] Documentar rotación de `SECRET_KEY`.
- [ ] Evaluar `whitenoise` para servir estáticos sin servidor web (ver 007).

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Creación a partir del estado real del repositorio |
