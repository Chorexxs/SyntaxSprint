# Plan técnico 002 — Autenticación y sesiones

| Campo | Valor |
| --- | --- |
| Spec | `specs/002-authentication/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Mantener el uso de `django.contrib.auth` y vistas función. Endurecer la entrada con
`request.POST.get(...)`, validadores de contraseña y `login_url` explícito. Extraer la
lógica de registro a una función auxiliar para poder probarla sin HTTP.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `backend/views.py` | Modificar | `.get()` defensivo, validadores, `login_url="login"`, mensajes con `messages.error`. |
| `backend/urls.py` | Sin cambios | Rutas existentes se conservan. |
| `templates/login.html` | Modificar | Mostrar mensajes con `role="alert"`. |
| `templates/signup.html` | Modificar | Mostrar lista de errores de validación. |
| `backend/tests.py` | Añadir | Tests de registro, login, logout y rutas protegidas. |

## 3. Diseño de datos

Se reutiliza `auth.User`. Sin migraciones.

| Campo | Origen | Validación |
| --- | --- | --- |
| `username` | POST | Único, requerido |
| `email` | POST | Único, requerido |
| `password` | POST | Validadores de Django |
| `password2` | POST | Igual a `password` |

## 4. Flujo de registro

```text
POST /signup
  ├─ campos ausentes ───────────────► 400 + mensaje
  ├─ password != password2 ────────► redirect /signup + mensaje
  ├─ email duplicado ──────────────► redirect /signup + mensaje
  ├─ username duplicado ───────────► redirect /signup + mensaje
  ├─ validate_password falla ──────► redirect /signup + errores
  └─ ok ─► create_user ─► authenticate ─► login ─► redirect /
```

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| Usar `UserCreationForm` | Validación incluida | Cambia el contrato POST actual | No (por ahora) |
| CBV `LoginView`/`LogoutView` | Menos código | Reestructura URLs y templates | No |
| Mantener vistas función + helpers | Cambio mínimo | Duplicación controlada | Sí |

## 6. Estrategia de pruebas

| Caso | Entrada | Esperado |
| --- | --- | --- |
| Registro OK | datos únicos | 302 a `/`, `User` creado, sesión activa |
| Email duplicado | email existente | 302 a `/signup`, sin nuevo usuario |
| Username duplicado | username existente | 302 a `/signup`, sin nuevo usuario |
| Contraseñas distintas | `a` vs `b` | 302 a `/signup`, sin usuario |
| Campos ausentes | `{}` | 400, sin excepción |
| Login OK | credenciales válidas | 302 a `/` |
| Login inválido | password errónea | 302 a `/login` |
| Perfil anónimo | sin sesión | 302 a `/login?next=/profile` |
| Logout | sesión activa | 302 a `/`, sesión cerrada |

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Cambiar mensajes rompe tests existentes | Baja | No hay tests aún |
| `login_url` con namespace | Baja | Usar nombre de URL `login` |
| Validadores bloquean contraseñas de prueba | Media | Usar `Str0ng-Pass!` en fixtures |

## 8. Orden de implementación

1. `.get()` y manejo de campos ausentes.
2. Validadores de contraseña.
3. `login_url` en vistas protegidas.
4. Mensajes accesibles en plantillas.
5. Tests de 007 fase 1.

## 9. Notas de despliegue

- Sin migraciones.
- Revisar que `LOGIN_URL` no sea necesario si todas las vistas declaran `login_url`.
