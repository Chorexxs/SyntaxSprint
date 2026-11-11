# Spec 002 — Autenticación y sesiones

| Campo | Valor |
| --- | --- |
| Estado | Implementada (backlog en `tasks.md`) |
| Versión | 1.0 |
| Depende de | 001-foundation |
| Archivos principales | `backend/auth_views.py`, `templates/login.html`, `templates/signup.html`, `syntax_sprint/urls.py` |

## 1. Contexto y problema

Para guardar resultados y ver el historial, el usuario necesita una cuenta. Hoy existe
registro, login y logout con el sistema de usuarios de Django, pero faltan validaciones
de contraseña, los redirects de rutas protegidas apuntan a una URL inexistente y no
todos los mensajes de error son visibles.

## 2. Objetivos

1. Registro con validación de duplicados y contraseñas.
2. Inicio y cierre de sesión claros y seguros.
3. Rutas protegidas que redirigen a un login existente.
4. Mensajes de error visibles y accesibles.

### No objetivos

- Login social (Google/GitHub).
- Recuperación de contraseña por email (backlog).
- Verificación de email.
- Roles o permisos personalizados.

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Visitante | Registrarse; iniciar sesión; ver errores de credenciales. |
| Usuario | Cerrar sesión; acceder a su perfil. |
| Administrador | Gestionar usuarios desde `/admin/`. |

## 4. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-002-01 | Cuando un visitante envía el formulario de registro con datos válidos, el sistema debe crear la cuenta e iniciar sesión automáticamente. | Alta |
| RF-002-02 | Cuando el email ya existe, el sistema debe rechazar el registro con un mensaje genérico que no revele si la cuenta existe. | Alta |
| RF-002-03 | Cuando el username ya existe, el sistema debe rechazar el registro con el mismo mensaje genérico que `RF-002-02`. | Alta |
| RF-002-04 | Cuando las contraseñas no coinciden, el sistema debe mostrar "Passwords do not match". | Alta |
| RF-002-05 | Cuando las credenciales son válidas, el sistema debe iniciar sesión y redirigir a `/`. | Alta |
| RF-002-06 | Cuando las credenciales son inválidas, el sistema debe mostrar "Invalid username or password". | Alta |
| RF-002-07 | Cuando un usuario autenticado solicita `/logout`, el sistema debe cerrar la sesión y redirigir a `/`. | Alta |
| RF-002-08 | Cuando un visitante solicita una ruta protegida, el sistema debe redirigir a `/login`. | Alta |
| RF-002-09 | Cuando el registro falla la validación de contraseña de Django, el sistema debe mostrar los motivos. | Media |
| RF-002-10 | Cuando el usuario envía campos vacíos u omitidos, el sistema debe responder 400 y no lanzar `KeyError`. | Alta |
| RF-002-11 | El sistema debe mostrar los mensajes de Django en login y signup. | Media |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| Email único | Comparación exacta, case-sensitive tal como está hoy. |
| Username único | Comparación exacta. |
| Contraseña | Debe pasar `AUTH_PASSWORD_VALIDATORS` (mínimo 8, no común, no numérica). |
| Contraseña repetida | `password == password2` obligatorio. |
| Sesión | `auth.login` tras registro o login correcto. |
| Logout | Solo por usuario autenticado y únicamente por POST; un GET responde 405. |
| Límite de intentos | 5 fallos por IP en 5 minutos; superado el límite se rechaza con mensaje genérico. |

## 6. Contratos

| Método | Ruta | Auth | Entrada | Salida | Errores |
| --- | --- | --- | --- | --- | --- |
| GET | `/login` | No | — | `login.html` | — |
| POST | `/login` | No | `username`, `password` | 302 → `/` | 302 → `/login` con mensaje |
| GET | `/signup` | No | — | `signup.html` | — |
| POST | `/signup` | No | `username`, `email`, `password`, `password2` | 302 → `/` | 302 → `/signup` con mensaje |
| GET | `/logout` | Sí | — | — | 405 `Method Not Allowed` |
| POST | `/logout` | Sí | — | 302 → `/` | 302 a login si no autenticado |

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-002-01 | Las contraseñas deben almacenarse con el hasher por defecto de Django (nunca en claro). |
| RNF-002-02 | Los formularios deben incluir `{% csrf_token %}`. |
| RNF-002-03 | Los mensajes de error deben ser visibles sin depender del color únicamente. |
| RNF-002-04 | El login debe resistir enumeración de usuarios sin revelar si el username existe. |

## 8. Criterios de aceptación

- **CA-002-01** Dado un visitante, cuando se registra con datos nuevos, entonces queda autenticado y ve la portada.
- **CA-002-02** Dado un email registrado, cuando intento registrarme, entonces vuelvo a `/signup` con el mensaje genérico de registro rechazado, sin revelar si el email existe.
- **CA-002-03** Dadas dos contraseñas distintas, cuando envío el formulario, entonces no se crea el usuario.
- **CA-002-04** Dado un usuario autenticado, cuando visito `/profile`, entonces veo mi perfil.
- **CA-002-05** Dado un visitante, cuando visito `/profile`, entonces soy redirigido a `/login` (no a `/accounts/login/`).
- **CA-002-06** Dado un POST de registro sin `email`, entonces la respuesta es 400 y no un error 500.

## 9. Fuera de alcance

- Recuperación de contraseña.
- 2FA.

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| `@login_required` sin `login_url` redirige a `/accounts/login/` (404) | Usuario bloqueado | T002-07 |
| No se ejecutan validadores de contraseña | Cuentas débiles | T002-06 |
| `request.POST["campo"]` lanza `KeyError` | Error 500 | T002-08 |
| Logout por GET | CSRF/logout forzado | T002-09 |
| Sin rate limiting | Fuerza bruta | Resuelto: 5 intentos/300 s por IP en `auth_views.py` |

## 11. Referencias de código

- `backend/auth_views.py` → `signup`, `login`, `logout`
- `templates/login.html`, `templates/signup.html`
- `syntax_sprint/syntax_sprint/settings.py` → `AUTH_PASSWORD_VALIDATORS`
