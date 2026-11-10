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

- [ ] **T008-05** Redactar el informe completo de línea base en `audits/code/2026-11-10-linea-base.md`.
  - Requisito: `RF-008-09`
  - Estado: parcial (resumen creado; falta revisión manual D1–D8 completa).

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

- [ ] **T008-09** Reducir las 61 líneas > 100 caracteres de `views.py` y las 7 de `script.js`.
  - Requisito: `RF-008-11`
  - DoD: `pylint` sin `line-too-long` en esos archivos.
  - Estado: parcial. `views.py` ya tiene 0 líneas > 100 (el catálogo se movió a
    `snippets.py`, que concentra 53). `script.js` conserva 7.

- [ ] **T008-10** Añadir anotaciones de tipo a las 9 funciones sin tipar.
  - Requisito: `RF-008-11`
  - Archivos: `backend/views.py`, `backend/models.py`
  - DoD: `code_metrics.py` reporta 0 funciones sin tipar.
  - Estado: pendiente. Siguen sin anotaciones `get_python_function`, `index`,
    `signup`, `login`, `logout`, `save_typing_test_result` y `profile` (7 funciones).

- [ ] **T008-11** Separar responsabilidades de `views.py`: catálogo → `snippets.py`,
  validación → helper, perfil → consulta única y paginada.
  - Requisitos: `RF-008-02`, `RF-008-12`
  - Coordina con: `T003-05`, `T005-07`, `T005-08`
  - DoD: `views.py` ≤ 120 líneas y sin lógica de negocio pesada.
  - Estado: pendiente. `views.py` tiene 326 líneas y el catálogo ocupa las líneas 43-180.

- [x] **T008-12** Reemplazar `innerHTML` en `script.js:201` por creación segura de nodos
  o `textContent`.
  - Requisito: `RF-008-11`
  - Archivos: `static/js/script.js`
  - DoD: `code_metrics.py` reporta 0 riesgos JS.
  - Evidencia: `renderCode` usa `document.createElement` + `replaceChildren`
    (`script.js:196-210`); no quedan asignaciones a `innerHTML`.

## Fase 3 — Testabilidad y escalabilidad

- [ ] **T008-13** Implementar la suite de pruebas (coordina con `T007-01`…`T007-04`).
  - Requisito: `RF-008-12`
  - DoD: cobertura ≥ 80 % en `backend/`.
  - Estado: parcial. La suite existe y pasa (26 tests), pero no se ha medido cobertura.

- [ ] **T008-14** Medir consultas del perfil y dejarlas en ≤ 5 por request.
  - Requisito: `RF-008-12`
  - Archivos: `backend/views.py`
  - DoD: medición documentada en el informe.

- [ ] **T008-15** Verificar que añadir un lenguaje solo requiere editar `snippets.py`
  (no la vista ni el JS).
  - Requisito: `RF-008-12`
  - DoD: prueba manual documentada.

- [ ] **T008-16** Añadir `code_metrics.py`, `isort` y `pylint` como quality gate en CI.
  - Requisitos: `RNF-008-02`, `RF-008-06`
  - Coordina con: `T007-11`
  - Estado: parcial. `isort` ya es bloqueante en CI; `pylint` se ejecuta como
    informativo (`continue-on-error`) y `code_metrics.py` aún no está en el workflow.
    Será bloqueante al cerrar `T008-09` y `T008-10`.

## Fase 4 — Reauditoría

- [ ] **T008-17** Repetir la auditoría tras cerrar los hallazgos ALTA y comparar scores.
  - Requisito: `RF-008-06`
  - DoD: nuevo informe en `audits/code/` con sección de comparación.

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
