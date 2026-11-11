# Auditoría de ciberseguridad — 2026-11-11 (post-analítica)

| Campo | Valor |
| --- | --- |
| Tipo | Ciberseguridad (spec 009) |
| Fecha | 2026-11-11 |
| Auditor | Agente (OpenCode) |
| Alcance | Repo completo: contenido, historial, configuración, endpoints, dependencias y GitHub |
| Commit auditado | `8e39fc0` (`main`) |
| Herramientas | `scan_secrets.py`, `pip-audit 2.10.1`, `manage.py check --deploy`, `curl`, API de GitHub |
| Resultado global | **MEDIO** — sin hallazgos CRÍTICOS ni ALTOS abiertos |

## 1. Alcance y exclusiones

- Incluido: archivos rastreados, historial de git, `settings.py`, endpoints, autenticación,
  autorización, CSRF, XSS, inyección, dependencias, cabeceras de producción, GitHub y
  datos personales en la BD y en logs.
- Excluido: pentesting ofensivo, infraestructura de Render/Cloudflare, revisión legal de
  privacidad y contenido de la base de datos (solo metadatos).

## 2. Resumen ejecutivo

No hay secretos reales en el contenido actual ni datos personales versionados: el
escaneo de contenido sale limpio, `.env` y `db.sqlite3` no aparecen en el historial,
`pip-audit` no encuentra vulnerabilidades y `check --deploy` da 0 issues con `DEBUG=False`.
Las tres alertas ALTAS del historial son falsos positivos documentados (configuración de
desarrollo y contraseñas dentro de fragmentos de código de ejemplo).

El riesgo residual es **MEDIO** y de disponibilidad, no de filtración: el rate limiting
del login depende de `REMOTE_ADDR` y de una caché en memoria, el admin no tiene límite de
intentos y los eventos de analítica crecen sin purga automática. Ninguna de estas
cuestiones expone datos de usuarios.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-016 | MEDIA | S11 Abuso | `backend/auth_views.py:81-105`, `settings.py` (sin `CACHES`), `gunicorn.conf.py:9-13` | Sonda local: 5 fallos permitidos, el 6.º bloquea; con el mismo `REMOTE_ADDR` un login correcto también queda bloqueado; otra IP entra. Caché = `LocMemCache` | Detrás del proxy de Render todas las peticiones pueden compartir IP: un atacante bloquea el login de todos 5 min; con varios workers el límite se multiplica | Usar `X-Forwarded-For` con `forwarded_allow_ips` acotado, caché compartida (Redis/BD) y clave `usuario+IP`; verificar la IP real en producción | M | Abierto |
| SEC-017 | MEDIA | S11 Abuso | `syntax_sprint/urls.py:9` (`/admin/`), `settings.py` | `curl /admin/` → 302 a login; Django admin no limita intentos y no hay 2FA | Fuerza bruta contra la cuenta de administrador si la contraseña es débil | Rate limiting (django-axes o middleware), 2FA y, si es posible, restringir por IP | M | Abierto |
| SEC-018 | MEDIA | S11 Abuso / S2 | `backend/analytics.py:22-32,83-86`, `snippet_views.py:15-30`, `render.yaml` | `GET /get_python_function` sin auth inserta una fila; la purga es manual y no hay cron en `render.yaml` | Crecimiento indefinido de la tabla y del disco con peticiones automatizadas | Programar `purge_analytics` (cron/schedule de Render) y limitar el endpoint por IP | S | Abierto |
| SEC-019 | BAJA | S7 Configuración | `backend/analytics.py:37,86`, `management/commands/purge_analytics.py:14-19` | `--days -1` deja el corte en el futuro y borra todos los eventos | Pérdida de métricas por un error de operación (comando de staff) | Validar `days >= 1` y rechazar valores no positivos | S | Abierto |
| SEC-020 | BAJA | S7 Configuración | `syntax_sprint/settings.py:185` | `SECURE_HSTS_SECONDS = 3600` | Ventana de downgrade mayor de lo necesario | Subir a 31 536 000 tras confirmar HTTPS estable | S | Abierto |
| SEC-021 | BAJA | S8 Dependencias / cadena de suministro | `.github/workflows/ci.yml:30,33,42` | Acciones referenciadas por etiqueta (`@v4`, `@v5`); API: `sha_pinning_required=false` | Una etiqueta comprometida ejecutaría código en CI | Fijar acciones por SHA y activar el requisito de pinning | S | Abierto |
| SEC-022 | INFO | S9 GitHub / S1 Secretos | `scan_secrets.py --history` | 3 ALTAS: `DEBUG` en `.env.example`, `DEBUG` en `settings.py` antiguo y una contraseña dentro de un snippet de `smtplib`/`paramiko` | Ninguna: no son credenciales reales; el valor está en fragmentos de ejemplo y no en el árbol actual | Mantener la clasificación de falso positivo documentada | — | Cerrado (FP) |
| SEC-023 | INFO | S5/S6/S7 Controles | Producción y configuración | `check --deploy` 0 issues; CSP sin `unsafe-inline`; HSTS, `nosniff`, `DENY`, `Referrer-Policy` y COOP presentes; cookies `Secure` + `SameSite=Lax`; `Host` falso → 403; HTTP → 301 HTTPS; 404/400 genéricos; cuerpo de 3 MB → 400 | Controles correctos | Mantener y revisar en cada cambio de configuración | — | Cerrado |

> Sin valores de secretos en este informe. Todos los datos personales revisados son de
> ejemplo (`@example.com`) o no están versionados.

## 4. Métricas

| Control | Valor | Umbral | Estado |
| --- | --- | --- | --- |
| Secretos en contenido | 0 | 0 | ✅ |
| Archivos sensibles rastreados | 0 | 0 | ✅ |
| `.env` / BD en historial | 0 | 0 | ✅ |
| Alertas del historial | 3 (FP) | 0 reales | ✅ |
| `check --deploy` (`DEBUG=False`) | 0 issues | 0 | ✅ |
| Vulnerabilidades en dependencias | 0 | 0 | ✅ |
| Repositorio | Privado | Privado | ✅ |
| GitHub Pages | 404 | 404 | ✅ |
| Rate limit de login | 5/300 s por IP | Activo | ⚠️ SEC-016 |
| Rate limit de admin | Ausente | Activo | ⚠️ SEC-017 |
| Retención de analítica | Manual | Automática | ⚠️ SEC-018 |
| Cuerpo máximo aceptado | 2,5 MB (400) | Acotado | ✅ |

## 5. Comparación con la auditoría anterior

| Métrica | 2026-11-11 (verificación) | Actual | Tendencia |
| --- | --- | --- | --- |
| CRÍTICAS | 0 | 0 | = |
| ALTAS reales | 0 | 0 | = |
| MEDIAS | 0 | 3 | ▲ (nuevas, por analítica y proxy) |
| Secretos en contenido | 0 | 0 | = |
| Vulnerabilidades | 0 | 0 | = |
| Tests | 39 | 52 | ▲ |
| Cobertura | 99 % | 99 % | = |

## 6. Acciones inmediatas (≤ 24 h)

1. Ninguna crítica. No hay rotación ni purga pendiente.
2. Verificar en producción qué valor toma `REMOTE_ADDR` (SEC-016) antes de ajustar el
   rate limiting.

## 7. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| SEC-016 | T009-29 | `specs/009-cybersecurity` |
| SEC-017 | T009-30 | `specs/009-cybersecurity` |
| SEC-018 | T009-31 | `specs/009-cybersecurity` |
| SEC-019 | T009-32 | `specs/009-cybersecurity` |
| SEC-020 | T009-33 | `specs/009-cybersecurity` |
| SEC-021 | T009-34 | `specs/009-cybersecurity` |

## 8. Comandos ejecutados

```bash
git status --short && git rev-parse --short HEAD
git ls-files | Select-String -Pattern "\.env$|\.sqlite3$|\.pem$|\.key$|id_rsa|\.log$|\.pyc$"
python specs/tools/scan_secrets.py
python specs/tools/scan_secrets.py --history --json
git log --all --oneline -- .env
git log --all --oneline -- "*db.sqlite3"
DEBUG=False python manage.py check --deploy
python -m pip_audit -r requirements.txt
python -m pip_audit -r requirements-dev.txt
curl -s https://syntaxsprint.onrender.com/            # cabeceras
curl -s https://syntaxsprint.onrender.com/login       # cookies
curl -H "Host: evil.example" https://syntaxsprint.onrender.com/   # 403
curl http://syntaxsprint.onrender.com/                # 301 -> https
manage.py shell                                       # sondas de rate limit y cuerpo grande
```

## 9. Limitaciones

- No se audita la infraestructura de Render/Cloudflare ni sus WAF.
- El estado de Secret Scanning/Push Protection no se pudo leer con el token disponible.
- La IP real que ve la aplicación detrás del proxy no se puede confirmar sin
  instrumentación (SEC-016 queda como riesgo a verificar).
- No se probaron ataques de fuerza bruta contra producción para no afectar al servicio.
- Una auditoría reduce el riesgo; no demuestra la ausencia total de vulnerabilidades.
