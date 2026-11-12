# Tareas 012 — Verificación en dos pasos del admin

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/012-admin-2fa/spec.md`

## Fase 1 — Base

- [x] **T012-01** Implementar TOTP con la biblioteca estándar y sus pruebas unitarias.
  - Requisitos: `RF-012-03`, `RNF-012-01`
  - Archivos: `backend/totp.py`, `backend/tests.py`
  - Evidencia: `code_for_counter`, `verify_code` (ventana ±1, `compare_digest`) y
    `provisioning_uri`; tests de ida y vuelta, replay, códigos malformados y URI.

- [x] **T012-02** Crear el modelo `AdminTOTP` y su migración.
  - Requisito: `RF-012-05`
  - Archivos: `backend/models.py`, `backend/migrations/0003_admintotp.py`
  - Evidencia: `makemigrations --check` sin cambios pendientes.

## Fase 2 — Implementación

- [x] **T012-03** Añadir la vista `/admin/2fa/`, las plantillas y la URL.
  - Requisitos: `RF-012-02`, `RF-012-04`
  - Archivos: `backend/two_factor.py`, `syntax_sprint/urls.py`, `templates/admin_2fa*.html`
  - Evidencia: formulario con CSRF, `autocomplete="one-time-code"` y mensaje de error;
    403 con instrucciones si falta el dispositivo.

- [x] **T012-04** Añadir `AdminTOTPMiddleware` y `ADMIN_TOTP_REQUIRED`.
  - Requisitos: `RF-012-01`, `RF-012-06`
  - Archivos: `backend/middleware.py`, `syntax_sprint/settings.py`
  - Evidencia: con la flag apagada el admin no cambia; encendida redirige a
    `/admin/2fa/` salvo rutas exentas (`login`, `logout`, `2fa`, `jsi18n`).

- [x] **T012-05** Crear el comando `enroll_admin_totp` con rotación y desactivación.
  - Requisito: `RF-012-05`
  - Archivos: `backend/management/commands/enroll_admin_totp.py`
  - Evidencia: crea/rota el secreto y muestra la URI; `--disable` lo elimina; rechaza
    usuarios que no son staff.

- [x] **T012-06** Escribir los tests de integración del flujo.
  - Requisitos: `CA-012-01`…`CA-012-07`
  - Archivos: `backend/tests.py`
  - Evidencia: `TwoFactorTests` con 14 casos (middleware, vista, replay, comandos).

## Fase 3 — Verificación

- [x] **T012-07** Verificar y documentar la activación.
  - Requisitos: `RNF-012-02`…`RNF-012-05`
  - Evidencia: `check` 0 issues; 74 tests OK; `isort` limpio; `pylint` 10.00/10;
    `code_metrics --strict` sin incumplimientos. Activación documentada en `DEPLOY.md`
    y `render.yaml`.

## Deuda técnica / Backlog

- [ ] Códigos de respaldo y recuperación de cuenta.
- [ ] Interfaz de enrolamiento con QR.
- [ ] Cifrado del secreto en reposo.
- [ ] 2FA para usuarios no staff.

## Historial

| Fecha | Cambio | Autor |
| --- | --- | --- |
| 2026-11-11 | Creación de la spec, el plan y las tareas | Agente |
| 2026-11-11 | Implementación completa, tests y documentación | Agente |
| 2026-11-12 | Límite de intentos en `/admin/2fa/` (RF-012-07, seguido en `T008-22`) | Agente |
| 2026-11-12 | Revocación de sesiones al rotar o desactivar el TOTP (RF-012-08, `T008-23`) | Agente |
