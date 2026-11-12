# Spec 012 — Verificación en dos pasos del admin

| Campo | Valor |
| --- | --- |
| Estado | Implementada |
| Versión | 1.1 |
| Depende de | 009-cybersecurity |
| Archivos principales | `backend/totp.py`, `backend/two_factor.py`, `backend/middleware.py`, `backend/management/commands/enroll_admin_totp.py` |

## 1. Contexto y problema

La auditoría `SEC-017` detectó que `/admin/` solo se protege con contraseña y rate
limiting. Una contraseña filtrada o reutilizada da acceso total a usuarios, resultados y
eventos de analítica. La spec 009 deja la 2FA en backlog.

## 2. Objetivos

1. Exigir un código TOTP a los usuarios staff antes de entrar en `/admin/`.
2. Permitir enrolar, rotar y desactivar el dispositivo desde la línea de comandos.
3. Rechazar códigos inválidos, caducados o reutilizados.
4. No añadir dependencias ni romper el admin si la función está desactivada.

### No objetivos

- 2FA para usuarios normales.
- Códigos de respaldo, SMS o email.
- Generación de QR en el navegador (se entrega la URI `otpauth://`).
- Recuperación automática de una cuenta bloqueada.

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Responsable del proyecto | Enrola o rota el TOTP del admin y activa la exigencia en producción. |
| Administrador | Inicia sesión con contraseña y después introduce el código de 6 dígitos. |
| Usuario normal | No se ve afectado: la 2FA solo aplica a staff. |

## 4. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-012-01 | Cuando `ADMIN_TOTP_REQUIRED` está activo y un staff entra en `/admin/` sin haber verificado el código, el sistema debe redirigirlo a `/admin/2fa/`. | Alta |
| RF-012-02 | Cuando el staff introduce un código TOTP válido, el sistema debe marcar la sesión como verificada y permitir el acceso al admin. | Alta |
| RF-012-03 | Cuando el código es inválido, caducado o ya usado, el sistema debe rechazarlo sin marcar la sesión. | Alta |
| RF-012-04 | Cuando un staff no tiene dispositivo confirmado, el sistema debe responder 403 con instrucciones de enrolamiento. | Media |
| RF-012-05 | El sistema debe ofrecer un comando para enrolar, rotar y desactivar el TOTP de un usuario staff. | Alta |
| RF-012-06 | Cuando `ADMIN_TOTP_REQUIRED` está desactivado, el admin debe funcionar como antes. | Alta |
| RF-012-07 | Cuando una IP supera 5 intentos de código en 300 s en `/admin/2fa/`, el sistema debe responder 429, no marcar la sesión y registrar el bloqueo. | Media |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| Algoritmo | TOTP RFC 6238: HMAC-SHA1, 6 dígitos, paso de 30 s, secreto base32 de 20 bytes. |
| Ventana | ±1 paso para tolerar desfase de reloj. |
| Replay | Se guarda el último contador aceptado; un código con contador ≤ al guardado se rechaza. |
| Comparación | `hmac.compare_digest` para evitar ataques de tiempo. |
| Sesión | Bandera `admin_totp_ok`; se rota la clave de sesión al verificar y desaparece al cerrar sesión. |
| Límite de intentos | 5 POST por IP y ventana de 300 s sobre la caché del rate limiting; se reinicia tras una verificación correcta. |
| Rutas exentas | `/admin/login/`, `/admin/logout/`, `/admin/2fa/`, `/admin/jsi18n/` y estáticos. |
| Desactivación | `enroll_admin_totp --disable` borra el dispositivo del usuario. |
| Secreto | Se guarda en la base de datos (necesario para verificar) y nunca se registra en logs. |

## 6. Contratos

### Rutas

| Método | Ruta | Auth | Respuesta |
| --- | --- | --- | --- |
| GET | `/admin/2fa/` | Staff | Formulario de código o 403 si no hay dispositivo |
| POST | `/admin/2fa/` | Staff | 302 a `/admin/` si el código es válido; 200 con error si no; 429 si se supera el límite |

### Comandos

| Comando | Efecto |
| --- | --- |
| `python manage.py enroll_admin_totp --username X` | Crea o rota el secreto y muestra la URI `otpauth://` |
| `python manage.py enroll_admin_totp --username X --disable` | Elimina el dispositivo |

### Modelo

`AdminTOTP`

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `user` | OneToOne | `CASCADE`, un dispositivo por staff |
| `secret` | `CharField(32)` | Base32 sin padding |
| `confirmed` | `BooleanField` | `True` tras el enrolamiento |
| `last_counter` | `BigIntegerField` | Último paso aceptado |
| `created_at` | `DateTimeField` | `auto_now_add` |

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-012-01 | Sin dependencias nuevas: `hmac`, `hashlib`, `base64`, `secrets` y `struct` de la biblioteca estándar. |
| RNF-012-02 | El secreto no aparece en logs, plantillas ni mensajes de error. |
| RNF-012-03 | Funciona igual en SQLite y PostgreSQL. |
| RNF-012-04 | La comprobación no añade más de una consulta por petición al admin. |
| RNF-012-05 | Con la función desactivada no hay redirecciones ni consultas extra. |

## 8. Criterios de aceptación

- **CA-012-01** Con la flag activa, un staff autenticado sin verificar que pide `/admin/` recibe 302 a `/admin/2fa/`.
- **CA-012-02** Un código válido en `/admin/2fa/` responde 302 a `/admin/` y marca la sesión.
- **CA-012-03** Un código incorrecto responde 200 con error y no marca la sesión.
- **CA-012-04** Reutilizar el mismo código responde 200 con error.
- **CA-012-05** Un staff sin dispositivo recibe 403 con instrucciones.
- **CA-012-06** `enroll_admin_totp` crea el dispositivo y `--disable` lo elimina.
- **CA-012-07** Con la flag desactivada, `/admin/` no redirige a la verificación.
- **CA-012-08** Tras 5 POST fallidos desde la misma IP, el sexto responde 429, no marca la sesión y deja un aviso en el log.

## 9. Fuera de alcance

- Interfaz de enrolamiento con QR.
- Códigos de respaldo y recuperación de cuenta.
- 2FA para usuarios no staff.
- WebAuthn o llaves físicas.

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Bloqueo del admin si se activa sin enrolar | Pérdida de acceso | Flag `False` por defecto y comandos de enrolar/desactivar documentados |
| Reloj desincronizado | Código rechazado | Ventana ±1 paso |
| Secreto en la BD | Acceso si se compromete la BD | Solo staff, sin logs; cifrado en reposo queda en backlog |
| Pérdida del dispositivo | Admin bloqueado | `--disable` desde la consola de Render |

## 11. Referencias de código

- `backend/totp.py` → generación y verificación
- `backend/two_factor.py` → vista de verificación
- `backend/middleware.py` → `AdminTOTPMiddleware`
- `backend/management/commands/enroll_admin_totp.py`
- `specs/009-cybersecurity/spec.md` — SEC-017
