# Tareas 009 — Auditoría de ciberseguridad y filtraciones

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/009-cybersecurity/spec.md`

## Fase 1 — Procedimiento y herramienta

- [x] **T009-01** Definir disparadores, alcance, categorías, severidades y reglas de oro.
  - Requisitos: `RF-009-01`, `RF-009-02`, `RF-009-13`
  - Archivos: `specs/009-cybersecurity/spec.md`

- [x] **T009-02** Crear `specs/tools/scan_secrets.py` sin dependencias y sin imprimir valores.
  - Requisitos: `RF-009-03`, `RF-009-12`
  - DoD: detecta `db.sqlite3` sin mostrar su contenido.

- [x] **T009-03** Ejecutar la línea base y documentarla (contenido, historial y `check --deploy`).
  - Requisitos: `RF-009-04`, `RF-009-05`, `RF-009-06`
  - Evidencia: 1 CRÍTICA (`db.sqlite3`), 13 BAJAS (`.pyc`), 6 warnings de Django.
  - DoD: sección 13 del spec y `audits/security/2026-11-10-linea-base.md`.

- [x] **T009-04** Añadir `*.sqlite3`, `__pycache__/` y `*.py[cod]` al `.gitignore`.
  - Requisito: `RF-009-04`
  - Archivos: `.gitignore`
  - DoD: un archivo nuevo de esos tipos no aparece como `??` en `git status`.

## Fase 2 — Remediación CRÍTICA (requiere autorización)

- [x] **T009-05** Dejar de rastrear `syntax_sprint/db.sqlite3` con `git rm --cached`.
  - Requisito: `RF-009-11`
  - Evidencia: `git status` muestra la baja; el archivo sigue en disco.
  - DoD: `git ls-files | grep db.sqlite3` vacío.

- [x] **T009-06** Rotar `SECRET_KEY` y forzar el reset de contraseñas de los 6 usuarios.
  - Requisito: `RF-009-14`
  - Evidencia: `SECRET_KEY` rotada en Render (86 chars). La BD local filtrada se eliminó y
    producción tiene 0 cuentas, por lo que no quedan contraseñas que resetear.

- [x] **T009-07** Purgar `db.sqlite3` del historial con `git filter-repo` y force-push coordinado.
  - Requisito: `RF-009-14`
  - Bloqueada por: autorización explícita y backup previo.
  - DoD: `git log --all --full-history -- syntax_sprint/db.sqlite3` vacío.

- [x] **T009-08** Decidir si el repositorio debe ser privado mientras se remedia.
  - Requisito: `RF-009-10`
  - Bloqueada por: decisión del usuario.
  - DoD: visibilidad documentada en el informe.

- [x] **T009-09** Dejar de rastrear los 13 `__pycache__/*.pyc`.
  - Requisito: `RF-009-04`
  - Evidencia: `scan_secrets.py` ya no reporta archivos `.pyc`.
  - DoD: `scan_secrets.py` reporta 0 archivos `.pyc`.

## Fase 3 — Configuración y aplicación

- [x] **T009-10** Añadir el bloque `if not DEBUG` con HTTPS, HSTS y cookies seguras
  (coordina con `T007-08`).
  - Requisito: `RF-009-06`
  - Evidencia: `check --deploy` con `DEBUG=False` → 0 issues.
  - DoD: `check --deploy` sin warnings W004/W008/W012/W016.

- [x] **T009-11** Sustituir `SECRET_KEY` débil por una clave aleatoria de ≥ 50 caracteres.
  - Requisito: `RF-009-06`
  - Evidencia: rotada en Render con 86 caracteres (auditoría 2026-11-10) y
    `check --deploy` con `DEBUG=False` → 0 issues (2026-11-11).

- [x] **T009-12** Asegurar `DEBUG=False` en producción.
  - Requisito: `RF-009-06`
  - Evidencia: la auditoría del 2026-11-10 verificó `DEBUG=False` en Render y
    `check --deploy` con `DEBUG=False` no reporta issues (2026-11-11). El `.env` local
    sigue en `True` a propósito para desarrollo.

- [x] **T009-13** Añadir `{% csrf_token %}` a la portada (coordina con `T004-08`).
  - Requisito: `RF-009-08`
  - Evidencia: test `test_index_sets_csrf_cookie`.

- [x] **T009-14** Cambiar el logout a POST con CSRF (coordina con `T002-09`).
  - Requisito: `RF-009-08`
  - Evidencia: tests `test_logout_requires_post` y `test_logout_post_clears_session`.

- [x] **T009-15** Reemplazar `innerHTML` en `script.js:201` por nodos seguros.
  - Requisito: `RF-009-08`
  - Evidencia: `code_metrics.py` ya no reporta `innerHTML`.

- [x] **T009-16** Añadir rate limiting al login.
  - Requisito: `RF-009-07`
  - Evidencia: test `test_login_rate_limit`.
  - Nota: `LocMemCache` es por proceso; para varios workers usar Redis/BD.

- [x] **T009-17** Verificar aislamiento por usuario en `/profile` y guardado.
  - Requisito: `RF-009-07`
  - Evidencia: test `test_user_cannot_see_other_results`.

## Fase 4 — Dependencias y GitHub

- [x] **T009-18** Ejecutar `pip-audit -r requirements.txt` en un entorno aislado.
  - Requisito: `RF-009-09`
  - Evidencia: 49 avisos antes; 0 después de actualizar.

- [x] **T009-19** Activar Secret Scanning, Push Protection y Dependabot en GitHub.
  - Requisito: `RF-009-10`
  - Evidencia: Dependabot configurado en `.github/dependabot.yml` (pip y GitHub Actions);
    Secret Scanning, Push Protection y alertas/actualizaciones activados por el
    responsable el 2026-11-11. No verificable sin acceso autenticado a GitHub.

- [x] **T009-20** Completar el checklist de 10 puntos de exposición en GitHub.
  - Requisito: `RF-009-10`
  - Estado: checklist documentado; Pages y visibilidad pendientes.
  - DoD: checklist firmado en `audits/security/`.

- [x] **T009-21** Verificar que logs y errores no exponen PII ni rutas internas.
  - Requisitos: `RF-009-11`, `RF-009-08`
  - Evidencia: con `DEBUG=False`, una vista que lanza `ValueError` devuelve 500 con el
    cuerpo genérico "Server Error (500)", sin traza ni rutas internas. No hay `print()`
    ni `logging` propios en `backend/` ni en `syntax_sprint/`.

## Fase 5 — Reauditoría

- [x] **T009-22** Reejecutar el escáner de contenido e historial y comparar con la línea base.
  - Requisitos: `RF-009-05`, `RF-009-14`
  - Estado: contenido e historial limpios; las 3 ALTAS restantes son falsos positivos
    documentados. Evidencia en `audits/security/2026-11-11-verificacion.md`.
  - DoD: nuevo informe en `audits/security/` sin hallazgos CRÍTICA.

## Fase 6 — Hallazgos de la auditoría completa (2026-11-10)

- [x] **T009-23** Despublicar GitHub Pages o cambiar el build para que no sirva
  `syntax_sprint/` (la BD y el código están accesibles por HTTP 200).
  - Requisito: `RF-009-10`
  - Evidencia: `curl -sI .../syntax_sprint/db.sqlite3` → 200, 139.264 bytes.
  - Bloqueada por: configuración del repositorio en GitHub.
  - DoD: la ruta devuelve 404 y se invalida la caché del sitio.

- [x] **T009-24** Actualizar dependencias vulnerables: Django 5.2.17+, certifi
  2026.10.18, idna 3.15, urllib3 2.8.0, sqlparse 0.6.0 y pylint 4.0.9 (dev).
  - Requisito: `RF-009-09`
  - Evidencia: `pip-audit` → 0 avisos.
  - DoD: `pip-audit` sin avisos en producción y tests en verde.

- [x] **T009-25** Corregir `ALLOWED_HOSTS` para descartar entradas vacías.
  - Requisito: `RF-009-06`
  - Evidencia: `_csv_env` descarta `''`; `check` OK.

- [x] **T009-26** Mitigar la enumeración de usuarios en el registro con un mensaje
  genérico y, opcionalmente, verificación por email.
  - Requisito: `RF-009-07`
  - Evidencia: test `test_signup_duplicate_email_is_generic`.

- [x] **T009-27** Invalidar las 8 sesiones de la base de datos y forzar el reset de las
  6 cuentas afectadas.
  - Requisito: `RF-009-14`
  - Evidencia: producción con 0 usuarios y 0 resultados; 1 sesión huérfana eliminada
    (`django_session` vacío). La BD local se recreó vacía.
  - DoD: `django_session` vacío y usuarios obligados a cambiar contraseña.

- [x] **T009-28** Añadir una política CSP y revisar cabeceras de seguridad.
  - Requisito: `RF-009-06`
  - Evidencia: `backend/middleware.py` añade `Content-Security-Policy` a todas las
    respuestas (incluidos 404), sin `'unsafe-inline'` ni CDN. Verificado en local con
    tema, Tailwind compilado y admin, sin violaciones en consola. Tests
    `SecurityHeadersTests`.

## Fase 7 — Hallazgos de la reauditoría (2026-11-11)

- [x] **T009-29** Resolver la IP real del cliente y compartir el contador de intentos.
  - Requisitos: `RF-009-07`, `RNF-009-02`
  - Archivos: `backend/auth_views.py`, `backend/ratelimit.py`, `gunicorn.conf.py`
  - Evidencia: `gunicorn.conf.py` usa `forwarded_allow_ips = "*"` (el servicio solo es
    accesible por el proxy de Render) y `client_ip()` lee `REMOTE_ADDR` ya reescrito.
    La clave del login es `login-attempts:<usuario>:<ip>`, así que un atacante ya no
    bloquea a todos los usuarios. Tests `test_login_rate_limit` y
    `test_login_rate_limit_is_per_username`.
  - DoD: IP real verificada en producción y bucket por usuario e IP. ✅
  - Residual: la caché por defecto es `LocMemCache`, así que con más de un worker
    gunicorn el contador se multiplica por proceso. Migrar a Redis o caché de BD queda
    en el backlog.

- [x] **T009-30** Proteger el admin contra fuerza bruta.
  - Requisito: `RF-009-07`
  - Archivos: `backend/middleware.py`, `syntax_sprint/settings.py`
  - Evidencia: `AdminLoginRateLimitMiddleware` limita `/admin/login/` a 5 POST por IP
    cada 5 minutos, responde 429 y reinicia el contador tras un login correcto. Tests
    `test_admin_login_returns_429_after_limit` y
    `test_admin_successful_login_resets_counter`. La 2FA ya está disponible en la spec
    012 (`ADMIN_TOTP_REQUIRED`).
  - DoD: rate limiting en `/admin/login/` y 2FA disponible. ✅

- [x] **T009-31** Programar la purga de analítica y limitar el endpoint de fragmentos.
  - Requisitos: `RF-009-11`, `RF-009-06`, `RF-003-09`
  - Archivos: `backend/analytics.py`, `backend/ratelimit.py`, `backend/snippet_views.py`
  - Evidencia: purga oportunista diaria (`maybe_purge_snippet_requests`) sin cron
    externo y límite de 120 peticiones/min por IP con 429 (`T003-11`). Sin cron ni
    coste extra en Render.
  - DoD: purga automática y endpoint acotado. ✅

- [x] **T009-32** Rechazar ventanas no positivas en `purge_analytics`.
  - Requisito: `RF-009-06`
  - Archivos: `backend/analytics.py`, `backend/management/commands/`
  - Evidencia: `purge_analytics --days 0` y `analytics_report --days -1` lanzan
    `CommandError`; `purge_snippet_requests` también valida `days >= 1`.
  - DoD: validación y prueba. ✅

- [x] **T009-33** Subir HSTS a un año tras verificar HTTPS estable.
  - Requisito: `RF-009-06`
  - Archivos: `syntax_sprint/settings.py`
  - Evidencia: `SECURE_HSTS_SECONDS = 31536000`; `check --deploy` con `DEBUG=False`
    sigue en 0 issues y producción ya servía todo por HTTPS.
  - DoD: HSTS de un año. ✅

- [x] **T009-34** Fijar las GitHub Actions por SHA.
  - Requisito: `RF-009-10`
  - Archivos: `.github/workflows/ci.yml`
  - Evidencia: `checkout@v4.4.0`, `setup-python@v5.6.0` y `setup-node@v4.4.0`
    referenciadas por SHA completo con la versión en comentario. CI en verde tras el
    cambio.
  - DoD: cada `uses:` apunta a un SHA completo. ✅

- [x] **T009-35** Compartir el contador de rate limiting entre workers.
  - Requisitos: `RF-009-07`, `RNF-009-02`
  - Archivos: `syntax_sprint/settings.py`, `backend/ratelimit.py`, `render.yaml`,
    `DEPLOY.md`
  - Evidencia: alias `shared` con `DatabaseCache` y `RATE_LIMIT_CACHE_ALIAS=shared` en
    Render; `createcachetable` en el arranque. Local y tests siguen con `LocMemCache`.
    Sonda con BD temporal: primera petición permitida, segunda bloqueada, reset y fila
    en `syntax_sprint_cache`.
  - DoD: con varios workers el contador se comparte. ✅

## Fase 8 — Reauditoría de código (2026-11-12)

- [ ] **T009-36** Limpiar del backlog la CSP y la 2FA ya implementadas.
  - Requisito: `RF-009-06`
  - Archivos: `specs/009-cybersecurity/tasks.md`
  - Evidencia: los ítems «2FA para el admin» y «Cabecera CSP» siguen abiertos aunque
    `T009-28`, `T009-30` y la spec 012 los cubren (AUD-029, INFO).
  - DoD: el backlog solo contiene trabajo pendiente real.

## Deuda técnica / Backlog

- [ ] Pre-commit hook con `scan_secrets.py` y `gitleaks`.
- [ ] Cifrado de backups y política de retención.
- [ ] Política de borrado de cuenta y datos.
- [ ] 2FA para el admin.
- [ ] Cabecera CSP.
- [ ] Notificación a usuarios ante brecha (procedimiento legal).
- [ ] Auditoría de dependencias en CI.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Creación del procedimiento, escáner y línea base crítica |
| 2026-11-10 | Auditoría completa: fuga activa confirmada en GitHub y GitHub Pages |
| 2026-11-10 | Historial purgado, force-push, repo privado y Pages despublicado |
| 2026-11-11 | Verificación local: PII fuera del repo, historial sin CRÍTICAS, `check --deploy` OK, 500 sin trazas y BD local saneada |
| 2026-11-11 | Producción sin cuentas ni sesiones; backup previo al despliegue y acciones de GitHub confirmadas |
| 2026-11-11 | CSP estricta y Tailwind compilado localmente (sin CDN ni `unsafe-inline`) |
| 2026-11-11 | Reauditoría post-analítica: 0 CRÍTICAS/ALTAS; 3 MEDIAS y 3 BAJAS nuevas |
| 2026-11-11 | Remediación completa: SEC-016…SEC-021 cerradas (rate limits, purga, HSTS, pinning) |
| 2026-11-11 | Caché compartida del rate limit (T009-35) y 2FA del admin (spec 012) |
