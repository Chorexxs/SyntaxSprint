# Verificación de la remediación — 2026-11-11

| Campo | Valor |
| --- | --- |
| Tipo | Seguridad (verificación de cierre) |
| Alcance | Contenido, historial, GitHub, configuración de despliegue y BD local |
| Commit base | `9de0453` (`main`) + rama `feature/accesibilidad-y-deuda` |
| Resultado | Filtraciones de PII y `SECRET_KEY` cerradas; quedan acciones del responsable |

## 1. Controles ejecutados

| Control | Comando reproducible | Resultado |
| --- | --- | --- |
| BD versionada | `git ls-files \| Select-String "db.sqlite3"` | Vacío |
| BD en el historial | `git log --all --full-history --oneline -- syntax_sprint/db.sqlite3` | Vacío |
| Secretos en contenido | `python specs/tools/scan_secrets.py` | Sin hallazgos |
| Secretos en historial | `python specs/tools/scan_secrets.py --history` | 0 CRÍTICAS; 3 ALTAS clasificadas como falsos positivos en `2026-11-10-auditoria-completa.md` §13 |
| `.env` en historial | `git log --all --oneline -- .env` | Vacío |
| Visibilidad del repo | `GET https://api.github.com/repos/Chorexxs/SyntaxSprint` sin auth | 403 (privado) |
| GitHub Pages | `HEAD .../SyntaxSprint/syntax_sprint/db.sqlite3` | 404 |
| Remoto `main` | `git ls-remote origin refs/heads/main` | `9de0453` (igual que local) |
| Configuración de producción | `DEBUG=False python manage.py check --deploy` | 0 issues |
| Error 500 sin trazas | Vista que lanza `ValueError` con `DEBUG=False` | 500 con "Server Error (500)", sin traza ni rutas internas |
| Logs de aplicación | Búsqueda de `print(`/`logging` en `backend/` y `syntax_sprint/` | Sin coincidencias |
| Suite de pruebas | `python manage.py test` | 31 tests OK |
| BD local con PII | `manage.py shell` antes de borrar | 6 usuarios / 31 resultados → eliminada y recreada vacía (0/0) |
| Producción | `insforge db query` sobre `auth_user` y `django_session` | 0 usuarios, 0 resultados, 0 sesiones |
| Backup previo al despliegue | `insforge db export -o <temp>/prod-backup-2026-11-11.sql` | 14.575 bytes, fuera del repositorio |

## 2. Acciones del responsable

| Acción | Estado |
| --- | --- |
| Revocar API keys de Render e InsForge | Hecho (2026-11-11) |
| Reset de contraseñas / aviso a usuarios | No aplica: producción tiene 0 cuentas y la BD local se eliminó |
| Secret Scanning, Push Protection y Dependabot | Hecho (2026-11-11) |
| Sesiones de producción | `django_session` vacío |
| Política CSP (`T009-28`) | Pendiente |

> Sin secretos ni datos personales en este informe.
