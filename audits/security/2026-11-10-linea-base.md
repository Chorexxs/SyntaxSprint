# Auditoría de ciberseguridad — Línea base 2026-11-10

| Campo | Valor |
| --- | --- |
| Tipo | Ciberseguridad y filtraciones |
| Fecha | 2026-11-10 |
| Auditor | Agente (procedimiento `specs/009-cybersecurity`) |
| Alcance | Archivos rastreados, historial, configuración Django, GitHub |
| Commit auditado | `d85ff1d` + cambios locales de `specs/` |
| Remoto | `https://github.com/Chorexxs/SyntaxSprint.git` |
| Visibilidad | **Por confirmar** (asumir pública hasta verificar) |
| Herramientas | `scan_secrets.py`, `manage.py check --deploy`, git, sqlite3 (solo conteos) |
| Resultado global | **CRÍTICO** |

## 1. Alcance y exclusiones

- Incluido: `git ls-files`, historial completo, `settings.py`, endpoints, dependencias
  declaradas y checklist de GitHub.
- Excluido: explotación activa, infraestructura del hosting y lectura de filas de la BD.
- Solo se consultaron **conteos** de la base de datos, nunca su contenido.

## 2. Resumen ejecutivo

El repositorio contiene una **fuga de datos personales**: `syntax_sprint/db.sqlite3`
está versionada en 15 commits e incluye 6 usuarios y 31 resultados, con emails y hashes
de contraseña. Además, el historial conserva una `SECRET_KEY` y dos contraseñas
hardcodeadas. La configuración actual sigue en modo desarrollo (`DEBUG=True`, sin HTTPS
ni cookies seguras) y el `SECRET_KEY` dispara el warning de clave insegura.

**Acción inmediata:** rotar credenciales, dejar de rastrear la BD, purgar el historial y
considerar el repositorio comprometido. La remediación requiere autorización del
responsable porque implica reescritura de historial y force-push.

## 3. Hallazgos

> Ningún valor sensible se reproduce en este informe. Las ubicaciones y longitudes son
> metadatos suficientes para localizar y rotar.

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SEC-001 | **CRÍTICA** | PII | `syntax_sprint/db.sqlite3` | Rastreada; 15 commits; 139.264 bytes; 6 usuarios; 31 resultados | Emails y hashes de contraseña públicos | `git rm --cached`, rotar, purgar historial | Abierto |
| SEC-002 | **CRÍTICA** | Secretos | `settings.py` @ `8c23ff0` | `scan_secrets.py --history`; longitud 66; prefijo `django-insecure-` | Falsificación de sesiones/tokens | Rotar `SECRET_KEY` y purgar | Abierto |
| SEC-003 | **CRÍTICA** | Secretos | `views.py` @ `6127fa4` | 2 contraseñas hardcodeadas (longitudes 13 y 8) | Reutilización/credenciales comprometidas | Rotar y purgar; forzar reset si son reales | Abierto |
| SEC-004 | ALTA | Configuración | `settings.py` @ `8c23ff0` y entorno actual | `check --deploy` W018 | Stack traces y settings expuestos | `DEBUG=False` en producción | Abierto |
| SEC-005 | ALTA | Secretos | Entorno actual | `check --deploy` W009 | Clave débil o prefijo inseguro | Generar clave aleatoria ≥ 50 chars | Abierto |
| SEC-006 | ALTA | Configuración | `settings.py` | W004, W008, W012, W016 | Secuestro de sesión por red | HTTPS, HSTS y cookies `Secure` | Abierto |
| SEC-007 | MEDIA | Higiene | 13 × `__pycache__/*.pyc` | `scan_secrets.py` | Rutas internas y ruido | `git rm -r --cached` + `.gitignore` | Abierto |
| SEC-008 | MEDIA | CSRF | `templates/index.html` | Sin `{% csrf_token %}` | POST inicial falla con 403 | Añadir token (T004-08) | Abierto |
| SEC-009 | MEDIA | Sesión | `backend/views.py` | Logout por GET | Logout forzado desde terceros | Cambiar a POST + CSRF | Abierto |
| SEC-010 | MEDIA | Abuso | `/login` | Sin rate limiting | Fuerza bruta y credential stuffing | Limitar intentos | Abierto |
| SEC-011 | MEDIA | XSS | `static/js/script.js:201` | `innerHTML = letters` | Inyección si el contenido no es confiable | Crear nodos de texto | Abierto |
| SEC-012 | BAJA | Dependencias | `requirements.txt` | `pip-audit` no instalado | CVEs sin detectar | Escanear en entorno aislado | Abierto |
| SEC-013 | INFO | Control positivo | `.env` | No rastreado ni en historial | — | Mantener | ✅ |
| SEC-014 | INFO | Control positivo | `backend/views.py` | Filtro por `request.user` | — | Mantener y probar | ✅ |
| SEC-015 | INFO | Control positivo | ORM / plantillas | Sin SQL crudo; autoescape activo | — | Mantener | ✅ |

## 4. Métricas

| Métrica | Valor | Esperado | Estado |
| --- | ---: | ---: | --- |
| Hallazgos CRÍTICOS | 3 | 0 | ❌ |
| Hallazgos ALTOS | 3 | 0 | ❌ |
| Hallazgos MEDIOS | 5 | 0 | ❌ |
| Archivos sensibles rastreados | 14 | 0 | ❌ |
| Contraseñas hardcodeadas en historial | 2 | 0 | ❌ |
| `SECRET_KEY` en historial | 1 | 0 | ❌ |
| Warnings `check --deploy` | 6 | 0 | ❌ |
| `.env` rastreado | 0 | 0 | ✅ |
| IDOR en perfil | 0 | 0 | ✅ |

## 5. Detalle de la fuga de la base de datos

| Dato | Valor |
| --- | --- |
| Archivo | `syntax_sprint/db.sqlite3` |
| Tamaño | 139.264 bytes |
| Commits que lo tocan | 15 |
| Usuarios | 6 |
| Resultados | 31 |
| Contenido sensible | Emails, hashes de contraseña, historial de actividad |
| Algoritmo de hash | Django PBKDF2 (por defecto) |
| Riesgo | Crackeo offline de contraseñas débiles + phishing por email |

> El hash PBKDF2 no es reversible, pero una contraseña débil puede crackearse offline.
> Debe asumirse que las 6 cuentas están comprometidas.

## 6. Acciones inmediatas (≤ 24 h)

1. **Rotar** `SECRET_KEY` en el entorno de producción.
2. **Forzar** el reset de contraseña de las 6 cuentas y de las 2 contraseñas hardcodeadas.
3. **Contener** el repositorio: pasar a privado hasta completar la purga (decisión).
4. **Dejar de rastrear** `db.sqlite3` y los `.pyc`.
5. **Purgar** el historial con `git filter-repo` y coordinar el force-push.
6. **Verificar** con `scan_secrets.py --history`.

## 7. Plan de remediación

| Paso | Acción | Responsable | Estado |
| --- | --- | --- | --- |
| 1 | Rotar `SECRET_KEY` | Proyecto | ⬜ |
| 2 | Reset de contraseñas | Proyecto | ⬜ |
| 3 | `git rm --cached` de BD y `.pyc` | Desarrollo | ⬜ |
| 4 | `git filter-repo` + force-push | Desarrollo | ⬜ |
| 5 | Activar secret scanning y Dependabot | Proyecto | ⬜ |
| 6 | Reauditar | Desarrollo | ⬜ |

> Los pasos 3–4 están documentados en `specs/009-cybersecurity/plan.md` y requieren
> autorización explícita y backup previo.

## 8. Checklist de GitHub

| Control | Estado |
| --- | --- |
| Repositorio privado mientras se remedia | ⬜ |
| `.gitignore` cubre `.env`, `*.sqlite3`, `__pycache__/`, `*.pyc` | ✅ (actualizado) |
| Historial sin secretos | ❌ |
| Actions sin secretos en logs | Sin workflows |
| Releases sin datos sensibles | Sin releases |
| Issues/PRs sin tokens | Sin evidencia |
| Secret scanning activo | Por confirmar |
| Dependabot activo | Por confirmar |
| Capturas sin credenciales | Sin evidencia de lo contrario |
| Forks asumidos inseguros | ⚠️ |

## 9. Tareas creadas

| Hallazgo | Tarea |
| --- | --- |
| SEC-001 | T009-05, T009-06, T009-07, T009-08 |
| SEC-002, SEC-003 | T009-06, T009-07 |
| SEC-004, SEC-005, SEC-006 | T009-10, T009-11, T009-12 |
| SEC-007 | T009-09 |
| SEC-008 | T009-13 |
| SEC-009 | T009-14 |
| SEC-010 | T009-16 |
| SEC-011 | T009-15 |
| SEC-012 | T009-18 |
| SEC-013…015 | Mantener y probar (T009-17) |

## 10. Comandos ejecutados

```bash
git ls-files
git log --all --full-history --oneline -- syntax_sprint/db.sqlite3
python specs/tools/scan_secrets.py
python specs/tools/scan_secrets.py --history
cd syntax_sprint && python manage.py check --deploy
python -c "import sqlite3; ... count(*) ..."   # solo conteos
```

## 11. Limitaciones

- No se verificó la visibilidad real del repositorio en GitHub (requiere sesión).
- No se ejecutó `pip-audit` (no instalado).
- No se explotó ninguna vulnerabilidad.
- No se leyeron filas de la base de datos; solo conteos agregados.
- El escáner histórico revisa los últimos 200 commits y solo líneas añadidas.
