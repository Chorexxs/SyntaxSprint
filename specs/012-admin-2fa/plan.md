# Plan técnico 012 — Verificación en dos pasos del admin

| Campo | Valor |
| --- | --- |
| Spec | `specs/012-admin-2fa/spec.md` |
| Estado | Aprobado |
| Autor | Agente |
| Última revisión | 2026-11-11 |

## 1. Enfoque

TOTP RFC 6238 implementado con la biblioteca estándar, sin dependencias. Un modelo
`AdminTOTP` guarda el secreto y el último paso aceptado. Un middleware comprueba la
bandera de sesión en las rutas del admin y redirige a una vista propia de verificación.
El enrolamiento se hace con un comando de gestión, no con una pantalla: así no hay que
exponer un flujo de alta antes de tener 2FA. Todo queda detrás de
`ADMIN_TOTP_REQUIRED` (por defecto `False`).

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `backend/totp.py` | Añadir | Secreto, código, verificación y URI `otpauth://`. |
| `backend/models.py` | Modificar | Modelo `AdminTOTP`. |
| `backend/migrations/0003_admintotp.py` | Añadir | Migración aditiva. |
| `backend/two_factor.py` | Añadir | Vista `/admin/2fa/` y constantes de sesión. |
| `backend/middleware.py` | Modificar | `AdminTOTPMiddleware`. |
| `backend/management/commands/enroll_admin_totp.py` | Añadir | Enrolar, rotar y desactivar. |
| `syntax_sprint/urls.py` | Modificar | Ruta `admin/2fa/`. |
| `syntax_sprint/templates/admin_2fa.html` | Añadir | Formulario del código. |
| `syntax_sprint/templates/admin_2fa_setup.html` | Añadir | Instrucciones si falta el dispositivo. |
| `syntax_sprint/settings.py` | Modificar | `ADMIN_TOTP_REQUIRED` y middleware. |
| `backend/tests.py` | Añadir | `TwoFactorTests`. |

## 3. Diseño de datos

```text
AdminTOTP
├── user: OneToOne(User, CASCADE, related_name="admin_totp")
├── secret: CharField(32)
├── confirmed: BooleanField(default=False)
├── last_counter: BigIntegerField(default=0)
└── created_at: DateTimeField(auto_now_add)
```

Migración necesaria: sí (`0003_admintotp`). Reversible: sí.

## 4. Contratos y flujos

```text
GET /admin/ (staff, sin bandera)
  → AdminTOTPMiddleware → 302 /admin/2fa/
GET /admin/2fa/ → formulario
POST /admin/2fa/ {code}
  → verify_code(secreto, código, last_counter)
      ├─ válido → guarda contador, session["admin_totp_ok"]=True, cycle_key → 302 /admin/
      └─ inválido → 200 con "Código incorrecto"
```

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| TOTP con biblioteca estándar | Sin dependencias, auditable | Hay que implementar y probar | Sí |
| `django-otp` | Probado, con QR | Dependencia nueva y capas extra | No |
| 2FA por email | Sin apps | Depende de correo y añade latencia | No |
| Restringir admin por IP | Simple | Frágil con IP dinámica y sin segundo factor | No |

## 6. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Unitario | Código válido, inválido, caducado y replay | `TestCase` |
| Unitario | URI de aprovisionamiento sin secretos en logs | `TestCase` |
| Integración | Middleware redirige/permite según sesión y flag | `Client` + `override_settings` |
| Integración | Vista de verificación marca la sesión | `Client` |
| Integración | Comando enrola y desactiva | `call_command` |

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Bloqueo del admin al activar la flag | Media | Flag apagada por defecto, enrolar antes y `--disable` |
| Desfase de reloj | Baja | Ventana ±1 |
| Regresión en login del admin | Media | Tests con flag on/off y exención de `/admin/login/` |
| Secreto en logs | Baja | No se registra y la plantilla no lo recibe |

## 8. Orden de implementación

1. `totp.py` + tests unitarios.
2. Modelo y migración.
3. Vista, plantillas y URL.
4. Middleware y setting.
5. Comando de enrolamiento.
6. Tests de integración.
7. Documentación y verificación.

## 9. Notas de despliegue

- Migraciones: `0003_admintotp` en el arranque.
- Variable nueva: `ADMIN_TOTP_REQUIRED` (`False` por defecto).
- Activación: `enroll_admin_totp --username <staff>` y después poner la variable a `True`.
- Rollback: poner la variable a `False`; el modelo puede quedarse.
