# Tareas 010 — Dependencias y actualización bajo demanda

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/010-dependencies/spec.md`

## Fase 1 — Especificación e inventario

- [x] **T010-01** Crear `spec.md`, `plan.md` y `tasks.md` con requisitos y criterios.
  - Requisito: `RF-010-01`
  - Archivos: `specs/010-dependencies/*`
  - DoD: la spec define el procedimiento sin decisiones pendientes.
  - Evidencia: requisitos `RF-010-01`…`RF-010-12` y criterios `CA-010-01`…`CA-010-06`.

- [x] **T010-02** Inventariar todas las dependencias y publicar la tabla en `plan.md`.
  - Requisito: `RF-010-02`
  - Archivos: `specs/010-dependencies/plan.md`
  - DoD: Python, CDN, runtime, CI e infraestructura aparecen con versión y acción.
  - Evidencia: secciones 3.1, 3.2 y 3.3 del plan; 22 paquetes de Python, 3 recursos
    de frontend y 5 de infraestructura.

## Fase 2 — Herramientas

- [x] **T010-03** Crear `specs/tools/check_dependencies.py` (stdlib) que liste las
  dependencias fijadas y marque las que no se usan.
  - Requisito: `RF-010-02`
  - Archivos: `specs/tools/check_dependencies.py`
  - DoD: `python specs/tools/check_dependencies.py` devuelve 0 y no necesita red.
  - Evidencia: `--strict` devuelve 0; comprueba pins exactos, duplicados, uso real y
    coherencia de la versión de Python. Sin dependencias externas ni red.

- [x] **T010-04** Documentar el formato de informe en `audits/dependencies/` y
  actualizar `audits/README.md`.
  - Requisito: `RF-010-10`
  - Archivos: `audits/dependencies/`, `audits/README.md`
  - DoD: existe la carpeta y las reglas del informe.

## Fase 3 — Limpieza de dependencias

- [x] **T010-05** Separar `requirements-dev.txt` (`pylint`, `pylint-django`, `isort`,
  `coverage`, `pip-audit`) de `requirements.txt`.
  - Requisito: `RF-010-12`
  - Archivos: `requirements.txt`, `requirements-dev.txt`, `render.yaml`,
    `.github/workflows/ci.yml`
  - DoD: producción instala solo lo necesario; CI instala ambos; tests en verde.
  - Evidencia: `requirements.txt` con 6 dependencias directas; `requirements-dev.txt`
    con `-r requirements.txt` + 5 herramientas; CI instala dev; README actualizado.

- [x] **T010-06** Eliminar `requests` y sus transitivas tras confirmar que no se usan.
  - Requisito: `RF-010-12`
  - Archivos: `requirements.txt`
  - DoD: búsqueda reproducible sin resultados y `manage.py check` + tests en verde.
  - Evidencia: `check_dependencies.py --strict` → "Sin uso: ninguna"; entorno limpio
    solo con `requirements.txt` → `check` 0 issues y 26 tests OK.

- [x] **T010-07** Unificar la versión de Python en una sola fuente (`render.yaml`,
  CI y documentación).
  - Requisitos: `RF-010-02`, `RNF-010-02`
  - Archivos: `render.yaml`, `.github/workflows/ci.yml`, `AGENTS.md`
  - DoD: no hay dos versiones distintas declaradas.
  - Evidencia: `.python-version` = 3.12.1; el CI lo lee con `python-version-file` sobre
    `ubuntu-24.04` (`T007-23`); `render.yaml` declara 3.12.1 y el verificador comprueba
    que coincidan.

- [x] **T010-08** Fijar la versión del CDN de Tailwind o migrar a build local.
  - Requisito: `RF-010-02`
  - Archivos: `syntax_sprint/templates/*.html`
  - Coordina con: `006`/`007` (eliminar CDN).
  - DoD: la versión usada está declarada explícitamente.
  - Evidencia: `package.json` fija `tailwindcss@3.4.17` y `npm run build:css` genera
    `static/css/tailwind.css`; `base.html` ya no carga el CDN. La 3.4.19 fijada antes no
    existía y fue corregida el 2026-11-11.

## Fase 4 — Automatización complementaria

- [x] **T010-09** Activar Dependabot para avisos y PRs de seguridad.
  - Requisito: `RF-010-04`
  - Archivos: `.github/dependabot.yml`
  - Coordina con: `T009-19`.
  - DoD: Dependabot abre PRs para `pip` y `github-actions`.
  - Evidencia: configuración semanal para `pip` (parches/menores agrupados) y mensual
    para `github-actions`; los saltos mayores de Django se ignoran y se aprueban a mano.

## Fase 5 — Primera ejecución

- [x] **T010-10** Ejecutar el procedimiento completo y generar el primer informe.
  - Requisitos: `RF-010-03`…`RF-010-10`
  - Archivos: `audits/dependencies/AAAA-MM-DD-actualizacion.md`
  - DoD: informe con inventario, `pip-audit`, grupos aplicados y verificación.
  - Evidencia: `audits/dependencies/2026-11-10-actualizacion.md`. Aplicados Django
    5.2.17→5.2.19 y pylint 4.0.9→4.1.3; `pip-audit` sin vulnerabilidades; mayores
    pendientes (Django 6.1.3, gunicorn 27.0.0, isort 9.0.2).

- [x] **T010-11** Registrar las dependencias de frontend en el inventario.
  - Requisitos: `RF-010-01`, `RF-010-05`
  - Archivos: `package.json`, `specs/010-dependencies/plan.md`
  - Evidencia: `vitest@2.1.9` y `jsdom@25.0.1` fijadas como dev; `npm run test:js`
    en verde y en CI. Vitest actualizado a 4.1.12 en `T008-30`, sin avisos de
    `npm audit`.

## Fase 4 — Runtime y Vercel (2026-11-12)

- [x] **T010-12** Fijar Python 3.12 (minor) para Render, CI y Vercel.
  - Requisitos: `RF-010-03`, `RF-010-06`
  - Archivos: `.python-version`, `render.yaml`, `.github/workflows/ci.yml`,
    `syntax_sprint/settings.py`, `DEPLOY.md`
  - Evidencia: Vercel/uv no encuentra el parche exacto `3.12.1`; con `3.12` el build
    continúa. `check_dependencies --strict` OK. Se añade `WSGI_APPLICATION`, los hosts
    de Vercel a `ALLOWED_HOSTS`/CSRF y `conn_max_age=0` en serverless.
  - DoD: Render, CI y Vercel comparten la minor 3.12 y `manage.py check --deploy` en
    verde. ✅

## Deuda técnica / Backlog

- [ ] Evaluar Vitest 5 cuando el CI migre a Node 22 (exige Node ≥ 22.12).
- [ ] Migrar a `requirements.in` + `pip-compile` con hashes.
- [ ] Evaluar Django 6.x (mayor, requiere plan de migración).
- [ ] Evaluar gunicorn 27 (mayor, requiere prueba de despliegue).
- [ ] Evaluar isort 9 (mayor, puede cambiar el formato de imports).
- [ ] Evaluar Renovate como alternativa a Dependabot.
- [ ] Auditar licencias de las dependencias.
- [ ] Generar un SBOM (`cyclonedx` o `syft`) en cada release.
- [ ] Revisar el soporte de Python 3.13 cuando Django lo certifique.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Creación de la spec, el plan y el inventario inicial |
| 2026-11-10 | Primera ejecución: requirements separados, `requests` eliminado, Tailwind fijado y Dependabot activado |
| 2026-11-12 | T010-12: Python 3.12 minor, WSGI y hosts de Vercel |
