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

- [!] **T009-05** Dejar de rastrear `syntax_sprint/db.sqlite3` con `git rm --cached`.
  - Requisito: `RF-009-11`
  - Bloqueada por: decisión del usuario sobre el repo y el historial.
  - DoD: `git ls-files | grep db.sqlite3` vacío.

- [!] **T009-06** Rotar `SECRET_KEY` y forzar el reset de contraseñas de los 6 usuarios.
  - Requisito: `RF-009-14`
  - Bloqueada por: acceso al entorno de producción y decisión de comunicación.
  - DoD: sesiones invalidadas y usuarios notificados.

- [!] **T009-07** Purgar `db.sqlite3` del historial con `git filter-repo` y force-push coordinado.
  - Requisito: `RF-009-14`
  - Bloqueada por: autorización explícita y backup previo.
  - DoD: `git log --all --full-history -- syntax_sprint/db.sqlite3` vacío.

- [!] **T009-08** Decidir si el repositorio debe ser privado mientras se remedia.
  - Requisito: `RF-009-10`
  - Bloqueada por: decisión del usuario.
  - DoD: visibilidad documentada en el informe.

- [ ] **T009-09** Dejar de rastrear los 13 `__pycache__/*.pyc`.
  - Requisito: `RF-009-04`
  - Archivos: `syntax_sprint/**/__pycache__/`
  - DoD: `scan_secrets.py` reporta 0 archivos `.pyc`.

## Fase 3 — Configuración y aplicación

- [ ] **T009-10** Añadir el bloque `if not DEBUG` con HTTPS, HSTS y cookies seguras
  (coordina con `T007-08`).
  - Requisito: `RF-009-06`
  - Archivos: `syntax_sprint/syntax_sprint/settings.py`
  - DoD: `check --deploy` sin warnings W004/W008/W012/W016.

- [ ] **T009-11** Sustituir `SECRET_KEY` débil por una clave aleatoria de ≥ 50 caracteres.
  - Requisito: `RF-009-06`
  - DoD: `check --deploy` sin W009.

- [ ] **T009-12** Asegurar `DEBUG=False` en producción.
  - Requisito: `RF-009-06`
  - DoD: `check --deploy` sin W018.

- [ ] **T009-13** Añadir `{% csrf_token %}` a la portada (coordina con `T004-08`).
  - Requisito: `RF-009-08`
  - Archivos: `templates/index.html`

- [ ] **T009-14** Cambiar el logout a POST con CSRF (coordina con `T002-09`).
  - Requisito: `RF-009-08`

- [ ] **T009-15** Reemplazar `innerHTML` en `script.js:201` por nodos seguros.
  - Requisito: `RF-009-08`
  - Archivos: `static/js/script.js`

- [ ] **T009-16** Añadir rate limiting al login.
  - Requisito: `RF-009-07`
  - DoD: 5 intentos fallidos en 1 minuto se bloquean temporalmente.

- [ ] **T009-17** Verificar aislamiento por usuario en `/profile` y guardado.
  - Requisito: `RF-009-07`
  - Archivos: `backend/tests.py`
  - DoD: test con dos usuarios que confirma que no se ven resultados ajenos.

## Fase 4 — Dependencias y GitHub

- [ ] **T009-18** Ejecutar `pip-audit -r requirements.txt` en un entorno aislado.
  - Requisito: `RF-009-09`
  - DoD: informe con CVEs y plan de actualización.

- [ ] **T009-19** Activar Secret Scanning, Push Protection y Dependabot en GitHub.
  - Requisito: `RF-009-10`
  - DoD: captura o estado documentado en el informe.

- [ ] **T009-20** Completar el checklist de 10 puntos de exposición en GitHub.
  - Requisito: `RF-009-10`
  - DoD: checklist firmado en `audits/security/`.

- [ ] **T009-21** Verificar que logs y errores no exponen PII ni rutas internas.
  - Requisitos: `RF-009-11`, `RF-009-08`
  - DoD: `DEBUG=False` muestra 500 genérico; logs sin emails.

## Fase 5 — Reauditoría

- [ ] **T009-22** Reejecutar el escáner de contenido e historial y comparar con la línea base.
  - Requisitos: `RF-009-05`, `RF-009-14`
  - DoD: nuevo informe en `audits/security/` sin hallazgos CRÍTICA.

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
