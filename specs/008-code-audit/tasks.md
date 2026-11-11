# Tareas 008 — Auditoría de código y arquitectura

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/008-code-audit/spec.md`

## Fase 1 — Procedimiento

- [x] **T008-01** Definir disparadores, alcance, dimensiones y severidades.
  - Requisitos: `RF-008-01`, `RF-008-02`, `RF-008-05`
  - Archivos: `specs/008-code-audit/spec.md`
  - DoD: el spec permite ejecutar la auditoría sin decisiones adicionales.

- [x] **T008-02** Crear `specs/tools/code_metrics.py` (complejidad, longitud, anidamiento,
  parámetros, imports, señales JS).
  - Requisito: `RF-008-11`
  - DoD: detecta `get_python_function` como función de 151 líneas.

- [x] **T008-03** Crear `specs/templates/audit-report.md` con formato de hallazgos y métricas.
  - Requisito: `RF-008-09`

- [x] **T008-04** Medir la línea base y documentarla en el spec.
  - Requisito: `RF-008-10`
  - Evidencia: `python specs/tools/code_metrics.py` → 16 archivos, 919 LOC, 9 funciones.
  - DoD: valores reales en la sección 12 del spec.

- [x] **T008-05** Redactar el informe completo de línea base en `audits/code/2026-11-10-linea-base.md`.
  - Requisito: `RF-008-09`
  - Evidencia: informe con las 9 secciones y la revisión manual D1–D8 añadida el
    2026-11-11 (observaciones por dimensión con evidencia `AUD-*`).

## Fase 2 — Hallazgos prioritarios

- [x] **T008-06** Refactorizar `get_python_function`: extraer catálogo y helper
  (coordina con `T003-05`).
  - Requisito: `RF-008-11`
  - Archivos: `backend/views.py`, `backend/snippets.py`
  - DoD: función ≤ 40 líneas y vista delgada.
  - Evidencia: `get_python_function` ocupa 16 líneas; el catálogo vive en
    `backend/snippets.py` y la vista solo valida el JSON y delega en `pick_snippet`.

- [x] **T008-07** Eliminar imports duplicados y sin usar en `views.py` (coordina con `T001-09`).
  - Requisito: `RF-008-11`
  - Archivos: `backend/views.py`
  - DoD: `pylint` sin `unused-import` ni `ungrouped-imports` en ese archivo.
  - Evidencia: `pylint --enable=unused-import,ungrouped-imports` no reporta avisos.

- [x] **T008-08** Ejecutar `isort` en los 5 archivos que fallan y añadir el check a CI.
  - Requisito: `RF-008-11`
  - Archivos: `backend/models.py`, `backend/urls.py`, `backend/views.py`,
    `syntax_sprint/settings.py`, `syntax_sprint/urls.py`
  - DoD: `isort --check-only syntax_sprint/` devuelve 0.
  - Evidencia: `isort --check-only syntax_sprint/` sin salida. El check en CI queda
    pendiente dentro de `T007-11`.

- [x] **T008-09** Reducir las 61 líneas > 100 caracteres de `views.py` y las 7 de `script.js`.
  - Requisito: `RF-008-11`
  - DoD: `pylint` sin `line-too-long` en esos archivos.
  - Evidencia: `code_metrics.py` ya no reporta líneas largas en `snippets.py` (53 → 0)
    ni en `script.js` (7 → 0); `pylint --enable=line-too-long` da 10.00/10 en
    `snippets.py`. El catálogo se reformateó sin cambiar sus 120 fragmentos y
    `node --check` valida el JS. Las 2 líneas de la migración se mantienen por ser
    autogeneradas (ver `plan.md` §11).

- [x] **T008-10** Añadir anotaciones de tipo a las 9 funciones sin tipar.
  - Requisito: `RF-008-11`
  - Archivos: `backend/views.py`, `backend/models.py`
  - DoD: `code_metrics.py` reporta 0 funciones sin tipar.
  - Evidencia: `code_metrics.py` → "Funciones sin anotaciones de tipo (sin tests): 0".

- [x] **T008-11** Separar responsabilidades de `views.py`: catálogo → `snippets.py`,
  validación → helper, perfil → consulta única y paginada.
  - Requisitos: `RF-008-02`, `RF-008-12`
  - Coordina con: `T003-05`, `T005-07`, `T005-08`
  - DoD: `views.py` ≤ 120 líneas y sin lógica de negocio pesada.
  - Evidencia: `views.py` queda en 7 líneas; se añaden `snippet_views.py`,
    `auth_views.py`, `result_views.py` y `validators.py`. El perfil usa una sola
    agregación. La paginación sigue en `T005-08`.

- [x] **T008-12** Reemplazar `innerHTML` en `script.js:201` por creación segura de nodos
  o `textContent`.
  - Requisito: `RF-008-11`
  - Archivos: `static/js/script.js`
  - DoD: `code_metrics.py` reporta 0 riesgos JS.
  - Evidencia: `renderCode` usa `document.createElement` + `replaceChildren`
    (`script.js:196-210`); no quedan asignaciones a `innerHTML`.

## Fase 3 — Testabilidad y escalabilidad

- [x] **T008-13** Implementar la suite de pruebas (coordina con `T007-01`…`T007-04`).
  - Requisito: `RF-008-12`
  - DoD: cobertura ≥ 80 % en `backend/`.
  - Evidencia: 26 tests y 98 % de cobertura (`views.py` 96 %, `models.py` 89 %).

- [x] **T008-14** Medir consultas del perfil y dejarlas en ≤ 5 por request.
  - Requisito: `RF-008-12`
  - Evidencia: `ProfileTests.test_query_budget` con `CaptureQueriesContext`: sesión,
    usuario, agregación, `COUNT` y página = **5 consultas**; documentado en la
    reauditoría.

- [x] **T008-15** Verificar que añadir un lenguaje solo requiere editar `snippets.py`
  (no la vista ni el JS).
  - Requisito: `RF-008-12`
  - Evidencia: `test_new_language_only_needs_catalog` añade `rust` al catálogo en tiempo
    de test y el endpoint lo devuelve sin tocar vista ni JS. La opción visible del
    selector vive en el markup de `index.html`; no hay lógica de lenguajes en la vista.

- [x] **T008-16** Añadir `code_metrics.py`, `isort` y `pylint` como quality gate en CI.
  - Requisitos: `RNF-008-02`, `RF-008-06`
  - Coordina con: `T007-11`
  - Evidencia: CI ejecuta `isort` (ya bloqueante), `pylint backend --rcfile=../.pylintrc`
    y `code_metrics.py --strict`; `code_metrics` falla ante funciones fuera de umbral,
    señales o funciones sin tipar (las migraciones quedan exentas). También compila
    Tailwind y falla si `tailwind.css` no está actualizado. Workflow validado como YAML y
    comandos replicados en local.

## Fase 4 — Reauditoría

- [x] **T008-17** Repetir la auditoría tras cerrar los hallazgos ALTA y comparar scores.
  - Requisito: `RF-008-06`
  - Evidencia: `audits/code/2026-11-11-reauditoria.md` → **8.8/10 (B)**, 0 ALTA y
    comparación con la línea base (3.8 → 8.8).

## Fase 5 — Hallazgos de la reauditoría (2026-11-11)

- [ ] **T008-18** Corregir el comentario obsoleto de `theme.js`.
  - Requisito: `RF-008-09`
  - Archivos: `static/js/theme.js`
  - Evidencia: el comentario dice "script inline"; `base.html:12` carga
    `theme-init.js` (AUD-013, BAJA).
  - DoD: el comentario describe el archivo externo.

- [ ] **T008-19** Configurar `LOGGING` con formato, nivel y handler de consola.
  - Requisitos: `RF-008-11`, `RF-008-04`
  - Archivos: `syntax_sprint/settings.py`
  - Evidencia: sin `LOGGING`, Django usa el default a stderr; `analytics.py:16` depende
    de ese default (AUD-014, BAJA).
  - DoD: logs con timestamp, nivel y logger de `backend`; verificado en local.

- [ ] **T008-20** Renombrar `_client_ip` para reflejar que lee `REMOTE_ADDR`.
  - Requisito: `RF-008-11`
  - Archivos: `backend/auth_views.py`
  - Evidencia: `auth_views.py:81-83` (AUD-015, BAJA; coordinado con `T009-29`).
  - DoD: nombre sin ambigüedad y tests en verde.

- [ ] **T008-21** Pasar un único `since` a las métricas del informe.
  - Requisito: `RF-008-03`
  - Archivos: `backend/analytics.py`
  - Evidencia: `build_report` recalcula la ventana por métrica (AUD-016, INFO).
  - DoD: una sola resolución de ventana por informe.

## Deuda técnica / Backlog

- [ ] Medir duplicación real con `pylint`/`jscpd`.
- [ ] Añadir análisis de CSS (tokens duplicados, selectores muertos).
- [ ] Medir Core Web Vitals del test.
- [ ] Revisar cobertura de ramas, no solo de líneas.
- [ ] Automatizar el informe en un comando único.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Creación del procedimiento, herramienta y línea base |
| 2026-11-10 | Verificación: imports limpios (`T008-07`), `isort` sin avisos (`T008-08`), `innerHTML` eliminado (`T008-12`) |
| 2026-11-10 | Catálogo extraído a `snippets.py`; `get_python_function` de 151 a 16 líneas (`T008-06`) |
| 2026-11-10 | Vistas separadas por dominio y validación extraída; `views.py` de 183 a 7 líneas (`T008-10`, `T008-11`) |
| 2026-11-11 | Catálogo y JS sin líneas > 100; migración excluida por ser autogenerada (`T008-09`) |
| 2026-11-11 | Perfil con 5 consultas y lenguajes extensibles; reauditoría 8.8 (B) (`T008-14`, `T008-15`, `T008-17`) |
| 2026-11-11 | Reauditoría post-analítica: 8.55 (B), 0 ALTA y 4 hallazgos menores |
