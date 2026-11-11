# Spec 009 — Auditoría de ciberseguridad y filtraciones

| Campo | Valor |
| --- | --- |
| Estado | Implementada (procedimiento listo) |
| Versión | 1.0 |
| Depende de | 000-overview, 007-quality-and-delivery |
| Archivos principales | `specs/tools/scan_secrets.py`, `specs/templates/audit-report.md` |
| Disparadores | "audita la seguridad", "auditoría de ciberseguridad", "revisa filtraciones", "¿se filtra algo?", "revisa las API keys" |

## 1. Contexto y problema

El repositorio parece público y ya contiene una base de datos SQLite versionada con
usuarios y resultados. Además, la configuración de producción está incompleta. Una fuga
de credenciales o datos personales en GitHub es irreversible: los bots escanean repos
públicos en minutos y los secretos quedan en el historial aunque se borren del último
commit.

Este spec define **cómo auditar la seguridad cuando el usuario lo indique**, con reglas
estrictas para no ampliar la fuga mientras se investiga.

## 2. Objetivos

1. Detectar secretos, credenciales y datos sensibles en el código y en el historial.
2. Detectar fallos de seguridad en autenticación, autorización y configuración.
3. Verificar que nada sensible se expone en GitHub público.
4. Producir un informe accionable sin revelar los valores encontrados.
5. Definir el protocolo de rotación y purga cuando hay una fuga real.

### No objetivos

- Pentesting ofensivo o explotación activa.
- Auditoría de infraestructura del proveedor (Render, Vercel, etc.).
- Cumplimiento legal formal (GDPR, SOC2).
- Análisis de malware en dependencias.

## 3. Cuándo se ejecuta

Solo bajo petición explícita del usuario:

- "audita la seguridad"
- "revisa si se filtra algo"
- "¿hay API keys expuestas?"
- "comprueba que no se suba información sensible a GitHub"
- "auditoría de ciberseguridad"

También debe ejecutarse **antes de hacer público un repositorio** o tras un cambio en
autenticación, configuración o dependencias.

## 4. Alcance

| Incluido | Excluido |
| --- | --- |
| Archivos rastreados por git | `venv/` y dependencias instaladas |
| Historial completo de git | Infraestructura del proveedor |
| `.gitignore` y archivos locales | Contenido de la BD (solo metadatos) |
| `settings.py` y configuración | Secretos reales (nunca se leen ni imprimen) |
| Endpoints y flujos de auth | Red externa |
| Dependencias declaradas | Pentesting activo |
| Metadatos de GitHub (visibilidad, Actions) | Repos de terceros |

## 5. Reglas de oro

1. **Nunca imprimir el valor de un secreto.** Ni en consola, ni en el informe, ni en
   capturas. Usar `<redacted>` o los últimos 4 caracteres como máximo.
2. **No pegar secretos en el chat, issues o PRs.**
3. **No commitear la corrección con el secreto dentro.** Rotar primero, limpiar después.
4. **La auditoría es de solo lectura** salvo que el usuario autorice la remediación.
5. **Si hay una fuga activa, el informe es privado** hasta completar la rotación.
6. **La rotación es obligatoria**: borrar el archivo no invalida el secreto.

## 6. Categorías de riesgo

| # | Categoría | Ejemplos |
| --- | --- | --- |
| S1 | Gestión de secretos | `SECRET_KEY`, API keys, tokens, contraseñas, claves privadas |
| S2 | Datos personales | Emails, usuarios, hashes, resultados, bases de datos |
| S3 | Autenticación | Login, sesiones, logout, validadores de contraseña |
| S4 | Autorización | IDOR, acceso a datos de otros usuarios, admin expuesto |
| S5 | Inyección | SQL, XSS, command injection, SSRF |
| S6 | CSRF / sesión | Tokens, cookies, `SameSite`, secure flags |
| S7 | Configuración | `DEBUG`, `ALLOWED_HOSTS`, HTTPS, HSTS, headers |
| S8 | Dependencias | CVEs, versiones sin fijar, paquetes abandonados |
| S9 | Exposición en GitHub | Historial, Actions, releases, issues, forks |
| S10 | Fuga de errores | Stack traces, settings, rutas internas |
| S11 | Abuso | Rate limiting, fuerza bruta, enumeración de usuarios |

## 7. Severidad y SLA

| Severidad | Criterio | SLA |
| --- | --- | --- |
| CRÍTICA | Secreto real expuesto, PII pública, auth bypass, RCE | ≤ 24 h + rotación inmediata |
| ALTA | Config insegura en producción, IDOR, XSS almacenado, dependencia crítica | ≤ 7 días |
| MEDIA | CSRF parcial, falta de rate limiting, error verboso, cookie sin `Secure` | ≤ 30 días |
| BAJA | Cabecera ausente, práctica mejorable sin impacto directo | ≤ 90 días |
| INFO | Control positivo o recomendación | Sin acción |

## 8. Procedimiento

### Paso 0 — Preparación

```bash
git status --short
git rev-parse --short HEAD
git remote -v
```

Anotar commit, ramas y visibilidad del repositorio (público/privado).

### Paso 1 — Inventario de archivos rastreados

```bash
git ls-files
python specs/tools/scan_secrets.py
```

Debe detectar al menos:

- `.env`, `*.sqlite3`, `*.pem`, `*.key`, `id_rsa`, `*.log`, `*.pyc`.
- Cualquier archivo de configuración con credenciales.

### Paso 2 — Escaneo de contenido

```bash
python specs/tools/scan_secrets.py --json
```

Patrones incluidos: `SECRET_KEY`, contraseñas, API keys, AWS, GitHub, Slack, Stripe,
Google, claves PEM, Bearer, URLs con credenciales, JWT, `DEBUG=True`, `ALLOWED_HOSTS=*`.

> El escáner imprime solo patrón, archivo y línea. Nunca el valor.

### Paso 3 — Historial de git

```bash
python specs/tools/scan_secrets.py --history
git log --all --full-history --oneline -- .env
git log --all --full-history --oneline -- "*db.sqlite3"
```

Un secreto borrado en el último commit **sigue estando en el historial**. Si aparece,
tratarlo como fuga activa.

### Paso 4 — Configuración Django

```bash
cd syntax_sprint
python manage.py check --deploy
```

Revisar manualmente:

| Control | Esperado |
| --- | --- |
| `DEBUG` | `False` en producción |
| `SECRET_KEY` | Larga, aleatoria, sin prefijo `django-insecure-`, fuera del repo |
| `ALLOWED_HOSTS` | Lista explícita, sin `*` |
| `SECURE_SSL_REDIRECT` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |
| `SECURE_HSTS_SECONDS` | > 0 en producción |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` |
| `X_FRAME_OPTIONS` | `DENY` |
| `Content-Security-Policy` | Presente en todas las respuestas y sin violaciones en consola |
| `CSRF_TRUSTED_ORIGINS` | Dominios reales |
| Admin | No expuesto sin auth y rate limiting |

### Paso 5 — Autenticación y autorización

- [ ] Registro valida duplicados y contraseña.
- [ ] Login no revela si el usuario existe.
- [ ] Logout invalida la sesión y no es GET.
- [ ] Rutas protegidas redirigen a login existente.
- [ ] Cada usuario solo ve sus resultados (`filter(user=request.user)`).
- [ ] No hay IDOR en parámetros (`?user_id=`).
- [ ] Admin requiere `is_staff`.
- [ ] Rate limiting en login.
- [ ] Sesión expira y rota al iniciar sesión.

### Paso 6 — Inyección y XSS

- [ ] ORM en todas las consultas; sin SQL concatenado.
- [ ] Plantillas con autoescape; sin `|safe` sobre datos de usuario.
- [ ] JS sin `innerHTML` con datos no confiables.
- [ ] Sin `eval`, `exec`, `document.write`.
- [ ] Sin comandos de shell con entrada de usuario.
- [ ] Sin `subprocess` con `shell=True` y datos externos.
- [ ] Sin peticiones salientes a URLs controladas por el usuario (SSRF).

### Paso 7 — Dependencias

```bash
# En un entorno aislado, no en el venv de producción
python -m pip install --user pip-audit
python -m pip_audit -r requirements.txt
```

Si no se puede instalar, revisar manualmente:

- Versiones fijadas (`==`).
- Paquetes sin mantenimiento.
- `pip list --outdated`.
- Avisos de GitHub Dependabot.

### Paso 8 — Exposición en GitHub

- [ ] Repositorio público: confirmar que no hay PII ni secretos.
- [ ] `.gitignore` cubre `.env`, `*.sqlite3`, `__pycache__/`, `*.pyc`, logs.
- [ ] Historial limpio (paso 3).
- [ ] Actions: sin `echo` de secretos, sin artefactos con `.env`.
- [ ] Releases y assets sin datos sensibles.
- [ ] Issues/PRs sin tokens pegados.
- [ ] Secret scanning y Dependabot activados.
- [ ] Forks: un secreto ya publicado no se puede recuperar; rotar.
- [ ] Capturas (`*.png`) sin credenciales visibles.
- [ ] Logs de despliegue sin variables de entorno.

### Paso 9 — Datos personales y retención

- [ ] La base de datos no está en el repo.
- [ ] Los backups no se publican.
- [ ] Los logs no guardan emails, contraseñas ni tokens.
- [ ] Los errores no muestran datos de otros usuarios.
- [ ] Existe una política de borrado de cuenta (backlog).

### Paso 10 — Informe

Crear `audits/security/AAAA-MM-DD-linea-base.md` con
`specs/templates/audit-report.md`. Reglas:

- ID `SEC-NNN`.
- Ubicación `archivo:línea` o `commit`.
- Evidencia sin valores: `<redacted>`.
- Impacto y probabilidad.
- Recomendación y esfuerzo.
- Si es CRÍTICA: rotación + purga + verificación.

### Paso 11 — Remediación (solo si el usuario autoriza)

Orden obligatorio:

1. **Contener**: revocar/rotar el secreto en el proveedor.
2. **Invalidar**: cerrar sesiones, forzar reset de contraseñas si aplica.
3. **Limpiar**: quitar el archivo del índice (`git rm --cached`).
4. **Purgar**: reescribir historial (`git filter-repo` o BFG) y force-push coordinado.
5. **Prevenir**: `.gitignore`, pre-commit, secret scanning.
6. **Verificar**: reescanear historial y contenido.

## 9. Protocolo ante un secreto expuesto

```text
1. DETENER. No copiar el valor.
2. Registrar: tipo de secreto, archivo, commit, antigüedad.
3. ROTAR en el proveedor (nueva clave, revocar la anterior).
4. Invalidar sesiones/tokens derivados.
5. Purgar del historial si el repo es público.
6. Activar secret scanning y pre-commit.
7. Informe privado + post-mortem.
8. Reauditar.
```

> Si el secreto estuvo público, **asumir compromiso**. Los bots indexan en minutos.

## 10. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-009-01 | Cuando el usuario use un disparador, el sistema debe ejecutar la auditoría completa. | Alta |
| RF-009-02 | La auditoría debe cubrir archivos rastreados, historial, configuración y GitHub. | Alta |
| RF-009-03 | El sistema debe detectar secretos por patrón sin imprimir su valor. | Alta |
| RF-009-04 | El sistema debe detectar archivos sensibles rastreados (`.env`, BD, claves, logs, `.pyc`). | Alta |
| RF-009-05 | El sistema debe revisar el historial de git en busca de secretos. | Alta |
| RF-009-06 | El sistema debe verificar la configuración de seguridad de Django. | Alta |
| RF-009-07 | El sistema debe verificar autenticación, autorización y aislamiento por usuario. | Alta |
| RF-009-08 | El sistema debe verificar CSRF, XSS, inyección y exposición de errores. | Alta |
| RF-009-09 | El sistema debe revisar dependencias vulnerables. | Media |
| RF-009-10 | El sistema debe verificar que no se exponga información sensible en GitHub. | Alta |
| RF-009-11 | El sistema debe evaluar el riesgo de PII en bases de datos y logs. | Alta |
| RF-009-12 | El informe debe enmascarar cualquier valor sensible. | Alta |
| RF-009-13 | Cada hallazgo debe tener severidad y SLA. | Alta |
| RF-009-14 | El sistema debe documentar rotación y purga para secretos expuestos. | Alta |

## 11. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-009-01 | Ningún valor de secreto se imprime, guarda ni transmite. |
| RNF-009-02 | El escaneo no modifica archivos ni el historial. |
| RNF-009-03 | El informe se escribe en español y con evidencia reproducible. |
| RNF-009-04 | El procedimiento debe tardar < 20 minutos. |
| RNF-009-05 | Si hay fuga activa, el informe no se publica hasta rotar. |

## 12. Criterios de aceptación

- **CA-009-01** Dado un `.env`, un `db.sqlite3` y un `.pyc` rastreados, el escáner los reporta.
- **CA-009-02** Dado un archivo con una API key de prueba, el escáner reporta patrón, archivo y línea, pero no el valor.
- **CA-009-03** Dado un secreto en un commit antiguo, `--history` lo detecta.
- **CA-009-04** `check --deploy` se ejecuta y sus warnings se clasifican.
- **CA-009-05** El informe usa `<redacted>` y no contiene valores reales.
- **CA-009-06** Todo hallazgo CRÍTICA incluye rotación, purga y verificación.
- **CA-009-07** La auditoría deja `git status` limpio salvo el informe.
- **CA-009-08** El checklist de GitHub está completo y firmado.

## 13. Línea base medida — 2026-11-10

| ID | Severidad | Hallazgo | Evidencia |
| --- | --- | --- | --- |
| SEC-001 | CRÍTICA | `syntax_sprint/db.sqlite3` versionada: 6 usuarios y 31 resultados | 15 commits; 139.264 bytes |
| SEC-002 | CRÍTICA | `SECRET_KEY` hardcodeada en el historial | `settings.py` @ `8c23ff0`; longitud 66; prefijo `django-insecure-` |
| SEC-003 | CRÍTICA | 2 contraseñas hardcodeadas en el historial | `views.py` @ `6127fa4`; longitudes 13 y 8 |
| SEC-004 | ALTA | `DEBUG=True` en historial y entorno actual | `check --deploy` W018 |
| SEC-005 | ALTA | `SECRET_KEY` actual dispara W009 (clave insegura) | `check --deploy` W009 |
| SEC-006 | ALTA | Sin HTTPS, HSTS ni cookies `Secure` | W004/W008/W012/W016 |
| SEC-007 | MEDIA | 13 archivos `__pycache__/*.pyc` rastreados | `scan_secrets.py` |
| SEC-008 | MEDIA | Portada sin `{% csrf_token %}`, el POST inicial puede dar 403 | `templates/index.html` |
| SEC-009 | MEDIA | Logout por GET | `backend/views.py` |
| SEC-010 | MEDIA | Sin rate limiting en login | Revisión manual |
| SEC-011 | MEDIA | `innerHTML` en `script.js:201` | `code_metrics.py` |
| SEC-012 | BAJA | Sin escaneo de dependencias (`pip-audit` no instalado) | `pip show` |
| SEC-013 | INFO | `.env` correctamente ignorado y sin historial | `git ls-files`; `git log` |
| SEC-014 | INFO | Resultados aislados por `request.user` | `backend/views.py` |
| SEC-015 | INFO | ORM y autoescape activos | Revisión manual |

**Riesgo global: CRÍTICO.** La base de datos debe salir del repositorio y del historial,
y las 6 cuentas más las 2 contraseñas hardcodeadas deben considerarse comprometidas.

> La auditoría completa del 2026-11-10 amplía esta línea base: el repositorio era público,
> GitHub Pages servía `db.sqlite3` (HTTP 200), la `SECRET_KEY` histórica estaba en uso y
> `pip-audit` detectaba 49 avisos. Se aplicó la remediación: BD y `.pyc` fuera del
> historial, clave histórica redactada, force-push, repo privado, Pages en 404,
> dependencias actualizadas y 26 tests. Sigue pendiente la rotación en producción
> (`SECRET_KEY`, sesiones y contraseñas). Ver
> `audits/security/2026-11-10-auditoria-completa.md`.

> Detalle completo en `audits/security/2026-11-10-linea-base.md`.

> Reauditoría post-analítica del 2026-11-11:
> `audits/security/2026-11-11-auditoria-post-analitica.md` → riesgo **MEDIO**, 0
> CRÍTICAS y 0 ALTAS reales, 3 MEDIAS y 3 BAJAS abiertas (SEC-016…SEC-021). Las 3
> ALTAS del historial se confirmaron como falsos positivos (SEC-022).
>
> Remediación del 2026-11-11: SEC-016, SEC-017, SEC-018, SEC-019, SEC-020 y SEC-021
> cerradas (`T009-29`…`T009-34`); no quedan hallazgos de seguridad abiertos.
> Además, caché compartida del rate limiting (`T009-35`) y 2FA del admin (spec 012).

## 14. Fuera de alcance

- Explotación de vulnerabilidades.
- Auditoría de la infraestructura del hosting.
- Revisión legal de privacidad.
- Análisis de malware.

## 15. Riesgos del propio proceso

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Copiar un secreto al informe | Amplía la fuga | Regla de enmascarado + revisión final |
| Purgar historial sin rotar | Secreto sigue válido | Rotar primero, siempre |
| Force-push sin coordinación | Pérdida de trabajo | Avisar, hacer backup, ventana acordada |
| Falsos positivos por patrones | Ruido | Marcar `[FP]` con justificación |
| Auditar solo el último commit | Falsa sensación de seguridad | Escanear historial siempre |

## 16. Referencias

- `specs/tools/scan_secrets.py`
- `specs/templates/audit-report.md`
- `audits/security/2026-11-10-linea-base.md`
- `specs/007-quality-and-delivery/spec.md`
- `specs/004-typing-engine/spec.md` (CSRF)
