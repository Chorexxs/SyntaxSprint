# Auditoría de seguridad — 2026-11-12 (prepublicación)

| Campo | Valor |
| --- | --- |
| Tipo | Ciberseguridad y filtraciones (spec 009) |
| Fecha | 2026-11-12 |
| Auditor | Agente (OpenCode) |
| Alcance | Árbol actual, historial completo (138 commits), configuración, dependencias y exposición en GitHub |
| Commit auditado | `4824abc` (`main`) |
| Herramientas | `scan_secrets.py` (contenido e historial), `git` (objetos, rutas y mensajes), `pip-audit`, `npm audit`, `manage.py check --deploy` |
| Resultado global | **BAJO** · 0 CRÍTICAS, 0 ALTAS, 0 MEDIAS, 4 BAJAS y 4 INFO |

## 1. Alcance y exclusiones

- Incluido: archivos rastreados, historial de todas las ramas y etiquetas, nombres de
  objetos, mensajes de commit, `.gitignore`, `settings.py`, `render.yaml`, workflows,
  dependencias y metadatos de GitHub.
- Excluido: pentesting, infraestructura de Render/InsForge, contenido de la BD local,
  issues/PRs/wiki de GitHub y valores reales de secretos (nunca se leen ni imprimen).

## 2. Resumen ejecutivo

**No hay API keys, tokens ni contraseñas reales en el árbol actual ni en el historial.**
Los tres avisos ALTOS del escáner histórico (cuatro líneas) son falsos positivos: dos
coincidencias de `password` dentro de fragmentos de código del catálogo
(`views.py @244996ca`) y dos `DEBUG=True` históricos en `.env.example` y `settings.py`.
No hay `.env`, bases de datos, `.pyc`, claves PEM ni backups en ningún commit: la purga
de 2026-11-10 fue efectiva.

La configuración de producción pasa `check --deploy` sin avisos, las dependencias tienen
0 CVEs y no hay SQL crudo, `innerHTML`, `eval`, `subprocess` ni peticiones salientes
peligrosas. Antes de hacer público el repositorio quedan **decisiones de PII** (email de
contacto, email del autor en los commits y una captura antigua con marcadores visibles)
y **prevención** (ampliar `.gitignore`). Ninguna es un secreto activo.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-023 | BAJA | PII | `README.md:138` | Email personal de contacto con dominio `gmail.com` | Queda visible al publicar; puede atraer spam | Usar alias/GitHub profile o aceptar el contacto público | S | Abierto |
| SEC-024 | BAJA | PII | Historial (138 commits) | `git log --format=%ae` → 2 dominios: uno `users.noreply.github.com` y otro `gmail.com` | GitHub mostrará el email del autor en cada commit | Activar email privado y reescribir autores a `noreply` antes de publicar, o aceptarlo | M | Abierto |
| SEC-025 | BAJA | PII / contexto | `381shots_so.png` (README:5) | Captura antigua de la app con la barra de marcadores visible; sin credenciales | Expone intereses personales y una UI obsoleta | Reemplazar por una captura limpia o eliminarla y ajustar el README | S | Abierto |
| SEC-026 | BAJA | Prevención | `.gitignore` | Cubre `.env`, `*.sqlite3`, `__pycache__`, coverage e `.insforge`, pero no `.env.*`, `*.log`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `backup.json`, `*.dump`, `.npmrc` ni `.pypirc` | Un despiste futuro podría versionar un secreto | Añadir esos patrones (con `!.env.example`) | S | Abierto |
| SEC-027 | INFO | [FP] Historial | `syntax_sprint/backend/views.py @244996ca` | Las coincidencias `password` están dentro de `"code": "..."` del catálogo de fragmentos (ejemplos de `smtplib` y `paramiko`) | Ninguno: no son credenciales de un servicio | Mantener como falso positivo documentado | — | Cerrado |
| SEC-028 | INFO | [FP] Historial | `.env.example @5fd70189`, `settings.py @1aef412f` | `DEBUG=True` en versiones antiguas | Ninguno: configuración histórica, no secreto | Nada; hoy producción usa `DEBUG=False` | — | Cerrado |
| SEC-029 | INFO | [FP] CI | `.github/workflows/ci.yml:24` | `SECRET_KEY` es un placeholder `ci-only-placeholder-…` | Ninguno: no se usa en producción | Mantener el nombre explícito | — | Cerrado |
| SEC-030 | INFO | Control positivo | `settings.py:203-216`, middleware, workflows | HTTPS/HSTS/cookies `Secure`, CSP, rate limit, 2FA disponible; 0 issues en `check --deploy`; 0 CVEs | — | Mantener y revisar tras publicar | — | Cerrado |

> Sin secretos ni datos personales en este informe: los emails se describen por dominio,
> nunca por dirección completa.

### Falsos positivos declarados

| Señal | Motivo |
| --- | --- |
| 3 avisos ALTOS de `scan_secrets.py --history` | Son SEC-027 y SEC-028: muestras de código y `DEBUG` histórico, no credenciales. |
| `SECRET_KEY` en CI y docs | Valores de ejemplo/placeholder, nunca de producción. |
| `DATABASE_URL` en `settings.py` | Es `config(...)`, no un valor literal. |

## 4. Métricas

| Control | Resultado | Estado |
| --- | --- | --- |
| Archivos sensibles rastreados (`.env`, BD, claves, `.pyc`, logs) | 0 | ✅ |
| Archivos sensibles en el historial | 0 (solo `.env.example`) | ✅ |
| Objetos históricos con nombres sensibles | 0 | ✅ |
| Secretos en contenido actual | 0 | ✅ |
| Secretos en historial | 3 ALTOS → todos falsos positivos | ✅ |
| Patrones en mensajes de commit | 0 | ✅ |
| `pip-audit` (prod y dev) | 0 vulnerabilidades | ✅ |
| `npm audit` | 0 vulnerabilidades | ✅ |
| `manage.py check --deploy` (`DEBUG=False`) | 0 issues | ✅ |
| SQL crudo / XSS / `eval` / `subprocess` / SSRF | 0 coincidencias | ✅ |
| `secrets.*`, `echo` o artefactos en Actions | 0 | ✅ |
| CI permissions | `contents: read` | ✅ |
| Visibilidad del repositorio | API 403 y Pages 404 (privado); confirmar en Settings | ⚠️ manual |
| PII (email contacto, email autor, captura) | 3 elementos | ⚠️ SEC-023…025 |

## 5. Comparación con la verificación anterior

| Métrica | 2026-11-11 | 2026-11-12 | Tendencia |
| --- | --- | --- | --- |
| Secretos reales | 0 | 0 | = |
| Archivos sensibles en historial | 0 | 0 | = |
| CVEs | 0 | 0 | = |
| `check --deploy` | 0 | 0 | = |
| Commits | 133 | 138 | ▲ |
| Hallazgos nuevos | — | 4 BAJAS de PII/prevención | ▲ (revisión prepublicación) |

La verificación de 2026-11-11 ya confirmó la rotación de `SECRET_KEY`, la revocación de
API keys de Render/InsForge, las sesiones vacías y 0 cuentas en producción. Esa rotación
sigue siendo la garantía real: un secreto que estuvo público no se recupera por purgar
el historial.

## 6. Acciones antes de hacer público

1. **Decidir PII**: email de contacto del README, email del autor en los commits y la
   captura `381shots_so.png` (SEC-023…025).
2. **Ampliar `.gitignore`** con `.env.*`, logs, claves, backups y credenciales npm/pip
   (SEC-026).
3. **Verificar en GitHub Settings**: secret scanning, push protection y Dependabot
   activos; Actions con permisos mínimos; Pages deshabilitado; sin releases con datos.
4. **Confirmar rotaciones** en Render e InsForge (hechas el 2026-11-11) y que no hay
   cuentas ni sesiones en producción.
5. **Tras publicar**: ejecutar de nuevo `scan_secrets.py --history` y revisar las alertas
   de GitHub; mantener el repo bajo observación las primeras 24 h.
6. Opcional: limpiar ramas Dependabot obsoletas y la rama local
   `feature/render-hardening` si ya no se usan.

## 7. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| SEC-023, SEC-024, SEC-025 | `T009-37` | `specs/009-cybersecurity` |
| SEC-026 | `T009-38` | `specs/009-cybersecurity` |
| Verificación manual de GitHub | `T009-39` | `specs/009-cybersecurity` |

## 8. Comandos ejecutados

```bash
git status --short && git rev-parse --short HEAD
# 4824abc; árbol limpio
python specs/tools/scan_secrets.py
# Sin hallazgos de secretos ni archivos sensibles.
python specs/tools/scan_secrets.py --history --max-commits 10000
# 3 ALTA históricas: clasificadas como falsos positivos (SEC-027/028)
git ls-files | Select-String "\.env|\.sqlite|\.pem|\.key|\.pyc|\.log|backup"
# vacío
git log --all --full-history --oneline -- .env "*db.sqlite3" "*.pyc" "*.pem"
# vacío
git rev-list --objects --all | Select-String "\.env$|\.sqlite|\.pem|\.key|\.pyc|backup"
# 0 objetos
pip-audit -r requirements.txt && pip-audit -r requirements-dev.txt
# No known vulnerabilities found
npm audit
# found 0 vulnerabilities
cd syntax_sprint && DEBUG=False python manage.py check --deploy
# System check identified no issues (0 silenced).
```

Versiones: Python 3.12.1, pip-audit del venv, Node 26.13.0, npm 12.2.2.

## 9. Limitaciones

- No se pudo consultar la API de GitHub (`403` sin autenticación); la visibilidad y los
  ajustes de seguridad se confirman en Settings (T009-39).
- No se revisaron issues, PRs, wiki, releases ni forks (el repo es privado).
- No se inspeccionan valores de secretos ni el contenido de la BD local.
- No es un pentest ni una auditoría legal de privacidad.
