# Tareas 002 — Autenticación y sesiones

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/002-authentication/spec.md`

## Fase 1 — Implementado

- [x] **T002-01** Implementar registro con `create_user`, auto-login y redirección a `/`.
  - Requisitos: `RF-002-01`, `RF-002-05`
  - Archivos: `backend/views.py`
  - DoD: usuario nuevo autenticado al terminar el registro.

- [x] **T002-02** Validar email y username duplicados con `messages.info`.
  - Requisitos: `RF-002-02`, `RF-002-03`

- [x] **T002-03** Validar coincidencia de contraseñas.
  - Requisito: `RF-002-04`

- [x] **T002-04** Implementar login/logout y proteger perfil y guardado de resultados.
  - Requisitos: `RF-002-05`…`RF-002-07`
  - Archivos: `backend/views.py`

- [x] **T002-05** Mostrar mensajes de Django en `login.html` y `signup.html`.
  - Requisito: `RF-002-11`

## Fase 2 — Endurecimiento

- [x] **T002-06** Aplicar `validate_password` antes de crear el usuario y mostrar todos los errores.
  - Requisito: `RF-002-09`
  - Archivos: `backend/views.py`, `templates/signup.html`
  - DoD: contraseña `12345678` se rechaza con mensaje explicativo.

- [x] **T002-07** Añadir `login_url="login"` a `profile` y `save_typing_test_result`.
  - Requisito: `RF-002-08`
  - Archivos: `backend/views.py`
  - DoD: visitante en `/profile` termina en `/login`, no en 404.

- [x] **T002-08** Sustituir `request.POST["..."]` por `.get()` y responder 400 si faltan campos.
  - Requisito: `RF-002-10`
  - Archivos: `backend/views.py`
  - DoD: POST vacío devuelve 400 sin traza.

- [x] **T002-09** Cambiar el logout a POST con formulario y `{% csrf_token %}`.
  - Requisito: `RF-002-07`
  - Archivos: `backend/views.py`, `templates/*.html`
  - DoD: GET `/logout` no cierra sesión; POST sí.

- [x] **T002-10** Normalizar email a minúsculas antes de comprobar duplicados.
  - Requisito: `RF-002-02`
  - Archivos: `backend/views.py`
  - DoD: `User@X.com` y `user@x.com` colisionan.

## Fase 3 — Verificación

- [x] **T002-11** Escribir tests de registro, login, logout y acceso anónimo.
  - Archivos: `backend/tests.py`
  - DoD: 9 casos del plan en verde.
  - Evidencia: `AuthTests` con 12 casos (incluye rate limit y contraseña débil);
    `manage.py test` → 26 tests OK.

- [x] **T002-12** Añadir `role="alert"` a los bloques de mensajes.
  - Requisito: `RNF-002-03`
  - Archivos: `templates/login.html`, `templates/signup.html`
  - Evidencia: `role="alert"` en `login.html:83` y `signup.html:103`.

## Deuda técnica / Backlog

- [x] Rate limiting por IP en login (django-axes o middleware propio).
  - Resuelto con caché de Django: 5 intentos / 300 s (`auth_views.py:15-16,97-105`),
    cubierto por `AuthTests` (`T002-11`).
- [ ] Recuperación de contraseña por email.
- [ ] Verificación de email.
- [x] Unificar los cuatro bloques de toggle de tema en `base.html` (ver 006).
  - Resuelto por `T006-06`: un único `#theme-toggle` y `static/js/theme.js`.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Auditoría del flujo actual y definición de endurecimiento |
| 2026-11-10 | Verificación contra código: 12 tests de `AuthTests` en verde |
| 2026-11-11 | `RF-002-02` y `RF-002-03` alineados con el mensaje genérico |

> `RF-002-02` y `RF-002-03` se actualizaron el 2026-11-11 para exigir un mensaje genérico
> que evite la enumeración de usuarios (`T009-26`), alineando la spec con el código.
