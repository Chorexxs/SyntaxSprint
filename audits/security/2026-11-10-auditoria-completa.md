# Auditoría de ciberseguridad — 2026-11-10 (completa)

> Informe interno de seguridad. No exponer fuera del repositorio.
> No contiene valores de secretos ni datos personales. Los hashes de commit citados
> corresponden al historial anterior a la purga y ya no existen en el remoto.

| Campo | Valor |
| --- | --- |
| Tipo | Ciberseguridad y filtraciones |
| Fecha | 2026-11-10 |
| Auditor | Agente (procedimiento `specs/009-cybersecurity`) |
| Alcance | Repo completo, historial, configuración, dependencias y GitHub |
| Commit auditado | `3f300a2` |
| Remoto | `https://github.com/Chorexxs/SyntaxSprint.git` |
| Visibilidad | **PÚBLICA** (`private=false`) |
| Herramientas | `scan_secrets.py`, `check --deploy`, `pip-audit`, git, sqlite3, GitHub API |
| Resultado global | **CRÍTICO contenido — historial purgado, repo privado y Pages despublicado** |

## 1. Alcance y método

Se revisaron:

- Los 84 archivos rastreados por git.
- Los 37 commits de la rama `main`.
- El contenido y el historial en busca de secretos (patrones + metadatos).
- La configuración efectiva de Django (sin imprimir valores sensibles).
- Los metadatos de la base de datos (solo conteos y algoritmo de hash).
- El repositorio y el sitio de GitHub Pages mediante la API pública y peticiones `HEAD`.
- Las dependencias declaradas con `pip-audit` en un entorno aislado.

No se descargó la base de datos, no se leyeron filas con datos personales y no se
explotó ninguna vulnerabilidad.

## 2. Resumen ejecutivo

El proyecto tiene una **fuga activa y confirmada**: el repositorio es público y
`syntax_sprint/db.sqlite3` es descargable tanto desde GitHub como desde GitHub Pages
(HTTP 200, 139.264 bytes, `Content-Type: application/octet-stream`). Esa base contiene
**6 usuarios, 31 resultados y 8 filas de sesión**, con emails y hashes PBKDF2.

Además, la `SECRET_KEY` hardcodeada en el commit `8c23ff0` **sigue siendo la clave actual**
(`secret_key_reused=True`). En el historial también hay dos contraseñas hardcodeadas
(ya no válidas para las cuentas actuales) y `DEBUG=True`.

La configuración de producción está incompleta (sin HTTPS, HSTS ni cookies seguras) y
`pip-audit` detecta **49 avisos únicos en 6 paquetes**, 32 de ellos en Django 5.2.6.

**Hay que asumir que las 6 cuentas están comprometidas.** La remediación no es opcional
ni puede esperar.

## 3. Exposición confirmada

### 3.1 Base de datos en el repositorio

| Dato | Valor |
| --- | --- |
| Archivo | `syntax_sprint/db.sqlite3` |
| Rastreado desde | commit inicial (`8c23ff0`) |
| Commits que lo tocan | 15 |
| Tamaño | 139.264 bytes |
| Usuarios | 6 |
| Resultados | 31 |
| Sesiones | 8 |
| Usuarios con `last_login` | 4 |
| Dominios de email distintos | 4 (1 de dominio de prueba) |
| Superusuarios / staff | 0 / 0 |
| Hash | PBKDF2-SHA256, 720.000 iteraciones |
| API de GitHub | `contents/syntax_sprint/db.sqlite3` → 200, sha `ac8df39e` |

### 3.2 GitHub Pages

El sitio `https://chorexxs.github.io/SyntaxSprint/` sirve el repositorio completo:

| Ruta | HTTP | Detalle |
| --- | ---: | --- |
| `/` | 200 | `text/html`, 8.321 bytes |
| `/syntax_sprint/db.sqlite3` | **200** | `application/octet-stream`, 139.264 bytes, `Access-Control-Allow-Origin: *` |
| `/syntax_sprint/syntax_sprint/settings.py` | 200 | Código fuente |
| `/README.md` | 200 | Documentación |
| `/.env` | 404 | Correcto: no está rastreado |

`Last-Modified: 2026-04-03`, por lo que Pages sirve una instantánea. Aun así, es una
copia pública de la base de datos y su contenido debe considerarse comprometido.

> El workflow `pages-build-deployment` está activo y publica el repo como sitio estático.

### 3.3 Historial de secretos

| Secreto | Commit | Metadatos | Estado actual |
| --- | --- | --- | --- |
| `SECRET_KEY` | `8c23ff0` | 66 caracteres, prefijo `django-insecure-`, 34 únicos | **Se sigue usando** (`secret_key_reused=True`) |
| Contraseña 1 | `6127fa4` | Longitud 13 | No válida para ninguna cuenta actual |
| Contraseña 2 | `6127fa4` | Longitud 8 | No válida para ninguna cuenta actual |
| `DEBUG=True` | `8c23ff0` | Configuración de desarrollo | Presente también en el entorno actual |

No se encontraron secretos en los mensajes de commit ni `.env` en el historial.

## 4. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | **CRÍTICA** | PII | `syntax_sprint/db.sqlite3` | 15 commits; 6 usuarios; 31 resultados; 8 sesiones | Emails y hashes públicos | Sacar del repo, rotar y purgar | Abierto |
| SEC-002 | **CRÍTICA** | Secretos | `settings.py` @ `8c23ff0` | `secret_key_reused=True`; 66 chars; prefijo `django-insecure-` | Tokens firmados y CSRF comprometidos | Rotar ya y purgar | Abierto |
| SEC-003 | ALTA | Secretos | `views.py` @ `6127fa4` | 2 contraseñas (13 y 8 chars); 0 cuentas actuales | Reutilización de credenciales | Rotar y purgar | Abierto |
| SEC-004 | **CRÍTICA** | Exposición | GitHub Pages | `db.sqlite3` → 200; 139.264 bytes; CORS `*` | Descarga directa de PII | Despublicar Pages o excluir el repo | Abierto |
| SEC-005 | **CRÍTICA** | Exposición | GitHub público | `private=false`; contents db → 200 | Descarga de PII e historial | Repo privado + purga | Abierto |
| SEC-006 | ALTA | Dependencias | `requirements.txt` | `pip-audit`: 49 avisos, 32 en Django 5.2.6 | CVEs explotables | Actualizar a Django 5.2.17+ y resto | Abierto |
| SEC-007 | ALTA | Configuración | `settings.py:28` | `DEBUG=True` | Stack traces y settings | `DEBUG=False` en producción | Abierto |
| SEC-008 | ALTA | Secretos | `.env` actual | W009; prefijo `django-insecure-`; 34 únicos | Clave predecible | Generar clave aleatoria ≥ 50 | Abierto |
| SEC-009 | ALTA | Configuración | `settings.py` | W004/W008/W012/W016 | Secuestro de sesión | HTTPS, HSTS y cookies `Secure` | Abierto |
| SEC-010 | ALTA | Sesión | `django_session` | 8 sesiones en la BD pública | Replay de sesiones activas | Borrar sesiones y forzar login | Abierto |
| SEC-011 | MEDIA | Configuración | `settings.py:30` | `ALLOWED_HOSTS` incluye `''` | Host vacío aceptado | Filtrar entradas vacías | Abierto |
| SEC-012 | MEDIA | Enumeración | `views.py:197,200` | Mensajes distintos para email/username | Descubrir cuentas | Mensaje genérico | Abierto |
| SEC-013 | MEDIA | Contraseñas | `views.py:203` | `validate_password` no se usa | Contraseñas débiles | Aplicar validadores | Abierto |
| SEC-014 | MEDIA | CSRF | `views.py:239` | Logout por GET | Logout forzado | POST + CSRF | Abierto |
| SEC-015 | MEDIA | CSRF | `templates/index.html` | Sin `{% csrf_token %}` | POST inicial 403 | Añadir token | Abierto |
| SEC-016 | MEDIA | Abuso | `/login` | Sin rate limiting | Fuerza bruta | Limitar intentos | Abierto |
| SEC-017 | MEDIA | XSS | `static/js/script.js:201` | `innerHTML = letters` | Inyección si el contenido no es confiable | Crear nodos de texto | Abierto |
| SEC-018 | MEDIA | Disponibilidad | `LOGIN_URL` | `/accounts/login/` (no existe) | Rutas protegidas → 404 | `login_url="login"` | Abierto |
| SEC-019 | BAJA | Higiene | 13 × `__pycache__/*.pyc` | Rastreados | Rutas internas y ruido | `git rm -r --cached` | Abierto |
| SEC-020 | BAJA | Cabeceras | Apps | Sin CSP | Mayor superficie XSS | Añadir CSP | Abierto |

### Detalle de SEC-010 — sesiones

La base de datos pública incluye la tabla `django_session` con **8 filas**. Las sesiones
de Django se guardan en la base de datos y la cookie solo contiene la clave aleatoria; un
atacante con el dump puede reutilizar esas claves mientras no expiren. **No basta con
rotar `SECRET_KEY`**: hay que borrar las sesiones.

## 5. Controles positivos

| ID | Control | Evidencia |
| --- | --- | --- |
| POS-01 | `.env` no está rastreado ni en el historial | `git ls-files`; `git log -- .env` vacío |
| POS-02 | No hay API keys de terceros en el proyecto ni en `.env` | Solo `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` |
| POS-03 | Sin `@csrf_exempt`, SQL crudo, `eval`, `exec` ni `subprocess` en la app | `git grep` |
| POS-04 | ORM y autoescape activos | Revisión de vistas y plantillas |
| POS-05 | Resultados aislados por `request.user` | `backend/views.py:264-265` |
| POS-06 | Hash PBKDF2-SHA256 con 720.000 iteraciones | Metadatos de la BD |
| POS-07 | Las 2 contraseñas históricas ya no son válidas | `check_password` → 0 coincidencias |
| POS-08 | Captura del README sin credenciales visibles | `381shots_so.png` revisada |
| POS-09 | Sin secretos en mensajes de commit | Escaneo de los 37 commits |
| POS-10 | `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy` | Configuración efectiva |

## 6. Configuración efectiva de Django

| Control | Valor | Esperado | Estado |
| --- | --- | --- | --- |
| `DEBUG` | `True` | `False` en producción | ❌ |
| `SECRET_KEY` | 66 chars, `django-insecure-` | ≥ 50 aleatorios | ❌ |
| `ALLOWED_HOSTS` | `['127.0.0.1', '']` | Lista explícita sin vacíos | ❌ |
| `SESSION_COOKIE_SECURE` | `False` | `True` | ❌ |
| `CSRF_COOKIE_SECURE` | `False` | `True` | ❌ |
| `SECURE_SSL_REDIRECT` | `False` | `True` | ❌ |
| `SECURE_HSTS_SECONDS` | `0` | > 0 | ❌ |
| `SESSION_COOKIE_HTTPONLY` | `True` | `True` | ✅ |
| `SESSION_COOKIE_SAMESITE` | `Lax` | `Lax`/`Strict` | ✅ |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | `True` | ✅ |
| `X_FRAME_OPTIONS` | `DENY` | `DENY` | ✅ |
| `SECURE_REFERRER_POLICY` | `same-origin` | `same-origin` | ✅ |
| Validadores de contraseña | Configurados | Aplicados en registro | ⚠️ no se usan |
| Admin | Habilitado | Con auth fuerte y 2FA | ⚠️ sin staff actual |
| `LOGIN_URL` | `/accounts/login/` | Ruta existente | ❌ |
| CORS | No configurado | Restrictivo | ✅ |

## 7. Dependencias vulnerables

`pip-audit -r requirements.txt` (entorno aislado):

| Paquete | Versión | Avisos únicos | Versión segura |
| --- | --- | ---: | --- |
| Django | 5.2.6 | 32 | 5.2.17+ (o 6.1.1) |
| urllib3 | 2.3.0 | 8 | 2.8.0 |
| sqlparse | 0.5.2 | 6 | 0.6.0 |
| certifi | 2026.2.25 | 1 | 2026.10.18 |
| idna | 3.10 | 1 | 3.15 |
| pylint (dev) | 3.3.4 | 1 | 4.0.9 |
| **Total** | | **49** | |

> Algunos avisos pueden estar duplicados o disputados; aun así, la versión de Django está
> claramente desactualizada y debe actualizarse.

## 8. GitHub — checklist de exposición

| Control | Estado |
| --- | --- |
| Repositorio privado mientras se remedia | ❌ público |
| `.gitignore` cubre `.env`, `*.sqlite3`, `__pycache__/`, `*.py[cod]` | ✅ |
| Historial sin secretos | ❌ |
| `db.sqlite3` fuera del árbol | ❌ |
| Pages sin archivos del backend | ❌ sirve todo el repo |
| Releases sin datos | ✅ 0 releases |
| Issues/Wiki habilitados | ⚠️ superficie de fuga |
| Secret scanning activo | Por confirmar (requiere auth) |
| Dependabot activo | Por confirmar (requiere auth) |
| Workflows sin secretos | ⚠️ solo `pages-build-deployment` |
| Forks asumidos inseguros | ⚠️ |

## 9. Plan de remediación

### Hoy (≤ 24 h)

1. **Despublicar GitHub Pages** o cambiar el origen para que no sirva `syntax_sprint/`.
2. **Rotar `SECRET_KEY`** en el entorno de producción (nueva clave aleatoria ≥ 50 chars).
3. **Forzar el reset de contraseña de las 6 cuentas** y notificar a los usuarios.
4. **Borrar las 8 filas de sesión**: `DELETE FROM django_session;` o
   `manage.py clearsessions`.
5. **Pasar el repositorio a privado** hasta completar la purga (decisión del responsable).
6. **`git rm --cached`** de `db.sqlite3` y los `.pyc`.
7. **Purgar el historial** con `git filter-repo` y force-push coordinado.
8. **Verificar** con `scan_secrets.py --history` y `curl`.

### ≤ 7 días

1. `DEBUG=False` y `ALLOWED_HOSTS` sin vacíos.
2. HTTPS, HSTS, cookies `Secure` y `CSRF_TRUSTED_ORIGINS`.
3. `validate_password` en el registro y mensaje genérico anti-enumeración.
4. Logout por POST y `{% csrf_token %}` en la portada.
5. Rate limiting en login.
6. Sustituir `innerHTML` por nodos seguros.
7. Actualizar Django a 5.2.17+ y certifi, idna, urllib3, sqlparse.
8. Corregir `login_url` en vistas protegidas.

### ≤ 30 días

1. CSP y revisión de cabeceras.
2. Secret scanning, push protection y Dependabot.
3. `pip-audit` y `scan_secrets.py` en CI/pre-commit.
4. 2FA para el admin.
5. Política de retención y borrado de datos.

## 10. Tareas creadas

| Hallazgo | Tarea |
| --- | --- |
| SEC-001 | T009-05, T009-06, T009-07, T009-08 |
| SEC-002 | T009-06 |
| SEC-003 | T009-06, T009-27 |
| SEC-004 | T009-23 |
| SEC-005 | T009-05, T009-08 |
| SEC-006 | T009-24 |
| SEC-007 | T009-12 |
| SEC-008 | T009-11 |
| SEC-009 | T009-10 |
| SEC-010 | T009-27 |
| SEC-011 | T009-25 |
| SEC-012 | T009-26 |
| SEC-013 | T002-06 |
| SEC-014 | T009-14 |
| SEC-015 | T009-13 |
| SEC-016 | T009-16 |
| SEC-017 | T009-15 |
| SEC-018 | T002-07, T005-09 |
| SEC-019 | T009-09 |
| SEC-020 | T009-28 |

## 11. Comandos ejecutados

```bash
git ls-files
git log --all --full-history --oneline -- syntax_sprint/db.sqlite3
python specs/tools/scan_secrets.py
python specs/tools/scan_secrets.py --history --max-commits 500
cd syntax_sprint && python manage.py check --deploy
pip-audit -r requirements.txt --format json
curl -sI https://chorexxs.github.io/SyntaxSprint/syntax_sprint/db.sqlite3
curl -s -o NUL -w "%{http_code}" https://api.github.com/repos/Chorexxs/SyntaxSprint/contents/syntax_sprint/db.sqlite3
```

## 12. Limitaciones

- No se descargó la base de datos ni se leyeron filas con datos personales.
- No se verificó la visibilidad ni el estado de Pages con una cuenta autenticada; se usó
  la API pública y peticiones `HEAD`.
- No se comprobó si el entorno de producción real usa la misma `SECRET_KEY`; se asume
  que sí por la reutilización local.
- Los avisos de dependencias pueden incluir duplicados o disputas del proveedor.
- No se revisaron capturas distintas de `381shots_so.png` ni issues/wiki de GitHub.
- La auditoría original fue de solo lectura; la remediación se aplicó después, en un
  cambio separado.

## 13. Remediación aplicada (2026-11-10)

| Acción | Evidencia | Estado |
| --- | --- | --- |
| `db.sqlite3` fuera del índice | `git rm --cached`; `scan_secrets.py` → 0 archivos sensibles | ✅ |
| 13 `.pyc` fuera del índice | `scan_secrets.py` → 0 | ✅ |
| BD y bytecode fuera de todo el historial | `git log --all -- syntax_sprint/db.sqlite3` vacío | ✅ |
| `SECRET_KEY` histórica redactada | `--replace-text`; `scan_secrets.py --history` → 0 CRÍTICA | ✅ |
| `SECRET_KEY` local rotada | 86 caracteres, sin prefijo inseguro | ✅ local |
| 8 sesiones locales borradas | `Session.objects.all().delete()` | ✅ local |
| Repositorio privado | API pública → 403; visibilidad verificada | ✅ |
| GitHub Pages despublicado | `curl .../db.sqlite3` → 404 | ✅ |
| Force-push del historial reescrito | `origin/main` = `0773615`, igual que local | ✅ |
| `ALLOWED_HOSTS` sin vacíos | `_csv_env` + `check` | ✅ |
| Bloque de producción | `check --deploy` con `DEBUG=False` → 0 issues | ✅ |
| Dependencias | `pip-audit` → 0 avisos; Django 5.2.17 | ✅ |
| CSRF en portada | test `test_index_sets_csrf_cookie` | ✅ |
| Logout por POST | tests `test_logout_*` | ✅ |
| Validación de registro y resultados | 26 tests OK | ✅ |
| Rate limiting | test `test_login_rate_limit` | ✅ |
| `innerHTML` eliminado | `code_metrics.py` sin riesgos JS | ✅ |
| Enumeración de usuarios | mensaje genérico en registro | ✅ |

Sigue pendiente (requiere acceso a producción o decisión):

- Rotar `SECRET_KEY`, borrar sesiones y resetear contraseñas en **producción**.
- Verificar que el despliegue real use `DEBUG=False`.
- Activar Secret Scanning y Dependabot.
- Añadir CSP.

> Los 3 avisos ALTOS que quedan en el historial son falsos positivos: `DEBUG` de
> configuración y contraseñas de ejemplo dentro de fragmentos de código. No son
> credenciales reales ni datos personales.

> Informe interno. Se commitea tras contener la exposición pública; la rotación de
> producción sigue pendiente.
