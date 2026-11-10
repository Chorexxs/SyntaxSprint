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

- [ ] **T008-06** Refactorizar `get_python_function`: extraer catálogo y helper
  (coordina con `T003-05`).
  - Requisito: `RF-008-11`
  - Archivos: `backend/views.py`, `backend/snippets.py`
  - DoD: función ≤ 40 líneas y vista delgada.

- [ ] **T008-07** Eliminar imports duplicados y sin usar en `views.py` (coordina con `T001-09`).
  - Requisito: `RF-008-11`
  - Archivos: `backend/views.py`
  - DoD: `pylint` sin `unused-import` ni `ungrouped-imports` en ese archivo.

- [ ] **T008-08** Ejecutar `isort` en los 5 archivos que fallan y añadir el check a CI.
  - Requisito: `RF-008-11`
  - Archivos: `backend/models.py`, `backend/urls.py`, `backend/views.py`,
    `syntax_sprint/settings.py`, `syntax_sprint/urls.py`
  - DoD: `isort --check-only syntax_sprint/` devuelve 0.

- [ ] **T008-09** Reducir las 61 líneas > 100 caracteres de `views.py` y las 7 de `script.js`.
  - Requisito: `RF-008-11`
  - DoD: `pylint` sin `line-too-long` en esos archivos.

- [ ] **T008-10** Añadir anotaciones de tipo a las 9 funciones sin tipar.
  - Requisito: `RF-008-11`
  - Archivos: `backend/views.py`, `backend/models.py`
  - DoD: `code_metrics.py` reporta 0 funciones sin tipar.

- [ ] **T008-11** Separar responsabilidades de `views.py`: catálogo → `snippets.py`,
  validación → helper, perfil → consulta única y paginada.
  - Requisitos: `RF-008-02`, `RF-008-12`
  - Coordina con: `T003-05`, `T005-07`, `T005-08`
  - DoD: `views.py` ≤ 120 líneas y sin lógica de negocio pesada.

- [ ] **T008-12** Reemplazar `innerHTML` en `script.js:201` por creación segura de nodos
  o `textContent`.
  - Requisito: `RF-008-11`
  - Archivos: `static/js/script.js`
  - DoD: `code_metrics.py` reporta 0 riesgos JS.

## Fase 3 — Testabilidad y escalabilidad

- [ ] **T008-13** Implementar la suite de pruebas (coordina con `T007-01`…`T007-04`).
  - Requisito: `RF-008-12`
  - DoD: cobertura ≥ 80 % en `backend/`.

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
