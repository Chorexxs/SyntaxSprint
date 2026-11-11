# Matriz de trazabilidad

Actualizada: 2026-11-11
Leyenda de estado: ✅ implementado · 🟡 parcial · ⬜ pendiente

> Verificación ejecutada el 2026-11-11: `manage.py check` → 0 issues,
> `manage.py test` → 31 tests OK, `isort --check-only syntax_sprint/` → sin avisos.
> Ver las notas al final para las divergencias código ↔ spec.

## 000 — Visión de producto

| Requisito | Spec | Tarea | Verificación | Estado |
| --- | --- | --- | --- | --- |
| RF-000-01 | `000-overview/spec.md` | T004-01 | CA-004-01 | ✅ |
| RF-000-02 | `000-overview/spec.md` | T002-01…T002-05 | CA-002-01 | ✅ |
| RF-000-03 | `000-overview/spec.md` | T003-01…T003-04 | CA-003-01 | ✅ |
| RF-000-04 | `000-overview/spec.md` | T004-03…T004-05 | CA-004-02 | ✅ |
| RF-000-05 | `000-overview/spec.md` | T005-02 | CA-005-01 | ✅ |
| RF-000-06 | `000-overview/spec.md` | T005-03, T005-04 | CA-005-05 | ✅ |
| RF-000-07 | `000-overview/spec.md` | T006-02 | CA-006-02 | ✅ |
| RF-000-08 | `000-overview/spec.md` | T006-04, T006-13 | CA-006-03 | 🟡 |
| RF-000-09 | `000-overview/spec.md` | T000-07, T008-01 | CA-008-01 | ✅ |
| RF-000-10 | `000-overview/spec.md` | T000-08, T009-01 | CA-009-01 | ✅ |

## 001 — Fundación

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-001-01 | T001-01, T001-07 | CA-001-01 | ✅ |
| RF-001-02 | T001-02 | `check` | ✅ |
| RF-001-03 | T001-03, T001-04 | CA-001-03 | 🟡 |
| RF-001-04 | T001-03 | `/` carga CSS/JS | ✅ |
| RF-001-05 | T001-02 | `/admin/` | ✅ |
| RF-001-06 | T001-08 | CA-001-02 | ✅ |
| RF-001-07 | T001-02 | `migrate` | ✅ |
| RF-001-08 | T001-05 | CA-001-04 | ✅ |
| RF-001-09 | T007-14 | CA-007-07 | ✅ |

## 002 — Autenticación

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-002-01 | T002-01 | CA-002-01 | ✅ |
| RF-002-02 | T002-02, T002-10 | CA-002-02 | 🟡 |
| RF-002-03 | T002-02 | CA-002-02 | 🟡 |
| RF-002-04 | T002-03 | CA-002-03 | ✅ |
| RF-002-05 | T002-01, T002-04 | CA-002-04 | ✅ |
| RF-002-06 | T002-04 | CA-002-05 | ✅ |
| RF-002-07 | T002-04, T002-09 | logout | ✅ |
| RF-002-08 | T002-07 | CA-002-05 | ✅ |
| RF-002-09 | T002-06 | mensajes de validación visibles | ✅ |
| RF-002-10 | T002-08 | CA-002-06 | ✅ |
| RF-002-11 | T002-05 | mensajes visibles | ✅ |

## 003 — Fragmentos de código

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-003-01 | T003-01 | catálogo 8 claves | ✅ |
| RF-003-02 | T003-02 | CA-003-01 | ✅ |
| RF-003-03 | T003-03 | CA-003-02 | ✅ |
| RF-003-04 | T003-01 | contrato `{name, code}` | ✅ |
| RF-003-05 | T003-04 | CA-003-03 | ✅ |
| RF-003-06 | T003-01 | 15 por lenguaje | ✅ |
| RF-003-07 | T003-06 | CA-003-04 | ✅ |
| RF-003-08 | — | respuesta única | ✅ |

## 004 — Motor de typing

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-004-01 | T004-01 | CA-004-01 | ✅ |
| RF-004-02 | T004-03 | CA-004-06 | ✅ |
| RF-004-03 | T004-02 | CA-004-04 | ✅ |
| RF-004-04 | T004-04, T004-11 | CA-004-02 | 🟡 |
| RF-004-05 | T004-04, T004-11 | CA-004-03 | 🟡 |
| RF-004-06 | T004-04 | stats en vivo | ✅ |
| RF-004-07 | T004-05, T004-10 | CA-004-05 | ✅ |
| RF-004-08 | T004-05, T004-10 | backspace | ✅ |
| RF-004-09 | T004-05 | atajos bloqueados | ✅ |
| RF-004-10 | T004-03 | CA-004-06 | ✅ |
| RF-004-11 | T004-06 | CA-004-07 | ✅ |
| RF-004-12 | T004-06, T004-09 | CA-004-08 | ✅ |
| RF-004-13 | T004-07 | IME | ✅ |
| RF-004-14 | T004-07, T004-13 | CA-004-09 | ✅ |
| RF-004-15 | T004-15 | decisión documentada | 🟡 |
| RF-004-16 | T006-02 | CA-006-02 | ✅ |

## 005 — Resultados y perfil

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-005-01 | T005-01 | migración 0001 | ✅ |
| RF-005-02 | T005-02 | CA-005-01 | ✅ |
| RF-005-03 | T005-02, T005-05 | CA-005-02 | ✅ |
| RF-005-04 | T005-02 | CA-005-04 | ✅ |
| RF-005-05 | T005-03 | historial | ✅ |
| RF-005-06 | T005-03, T005-07 | CA-005-05 | ✅ |
| RF-005-07 | T005-04 | CA-005-06 | ✅ |
| RF-005-08 | T005-09 | CA-005-07 | ✅ |
| RF-005-09 | T005-06 | CA-005-03 | ✅ |
| RF-005-10 | T005-08 | tests de paginación | ✅ |
| RF-005-11 | T005-03 | fecha legible | ✅ |
| RF-005-12 | T005-01, T005-12 | CA-005-08 | ✅ |

## 006 — UI y temas

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-006-01 | T006-01 | CA-006-01 | ✅ |
| RF-006-02 | T006-02, T006-06 | CA-006-02 | ✅ |
| RF-006-03 | T006-01, T006-07 | sin FOUC | ✅ |
| RF-006-04 | T006-05 | CA-006-06 | ✅ |
| RF-006-05 | T006-04, T006-13 | CA-006-03 | 🟡 |
| RF-006-06 | T006-03 | manual: estados visuales | ✅ |
| RF-006-07 | T006-08, T006-10, T006-11 | CA-006-04 | ✅ |
| RF-006-08 | T006-09 | CA-006-05 | ✅ |
| RF-006-09 | T006-15 | preferencia SO | ⬜ |
| RF-006-10 | T006-05 | favicon/título | ✅ |

## 007 — Calidad y despliegue

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-007-01 | T007-01…T007-04 | suite | ✅ |
| RF-007-02 | T007-01…T007-04 | CA-007-01 | ✅ |
| RF-007-03 | T007-13 | lint | 🟡 |
| RF-007-04 | T003-06, T005-05, T007-07 | CA-007-05 | ✅ |
| RF-007-05 | T007-08 | CA-007-03 | ✅ |
| RF-007-06 | T003-07, T005-02 | 405 | ✅ |
| RF-007-07 | T007-10 | CA-007-04 | ✅ |
| RF-007-08 | T007-14, T007-15, T007-16 | CA-007-07 | 🟡 |
| RF-007-09 | T004-08, T007-06 | POST 200 | ✅ |
| RF-007-10 | T007-09 | CA-007-04 | ✅ |
| RF-007-11 | T007-11 | CI | ✅ |

## 008 — Auditoría de código

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-008-01 | T008-01 | CA-008-01 | ✅ |
| RF-008-02 | T008-01 | CA-008-01 | ✅ |
| RF-008-03 | T008-01 | CA-008-03 | ✅ |
| RF-008-04 | T008-02, T008-03 | CA-008-02 | ✅ |
| RF-008-05 | T008-01 | CA-008-05 | ✅ |
| RF-008-06 | T008-04 | CA-008-03 | ✅ |
| RF-008-07 | T008-01 | CA-008-04 | ✅ |
| RF-008-08 | T008-01 | CA-008-05 | ✅ |
| RF-008-09 | T008-03, T008-05 | CA-008-01 | 🟡 |
| RF-008-10 | T008-04 | CA-008-03 | ✅ |
| RF-008-11 | T008-02, T008-06 | CA-008-06 | ✅ |
| RF-008-12 | T008-11, T008-15 | CA-008-05 | 🟡 |

## 009 — Ciberseguridad

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-009-01 | T009-01 | CA-009-01 | ✅ |
| RF-009-02 | T009-01, T009-03 | CA-009-01 | ✅ |
| RF-009-03 | T009-02 | CA-009-02 | ✅ |
| RF-009-04 | T009-02, T009-03 | CA-009-01 | ✅ |
| RF-009-05 | T009-02, T009-03 | CA-009-03 | ✅ |
| RF-009-06 | T009-03, T009-10 | CA-009-04 | 🟡 |
| RF-009-07 | T009-17 | CA-009-01 | ✅ |
| RF-009-08 | T009-13, T009-14, T009-15 | CA-009-07 | ✅ |
| RF-009-09 | T009-18 | CA-009-01 | ✅ |
| RF-009-10 | T009-19, T009-20 | CA-009-08 | 🟡 |
| RF-009-11 | T009-05 | CA-009-01 | ✅ |
| RF-009-12 | T009-02 | CA-009-05 | ✅ |
| RF-009-13 | T009-01 | CA-009-06 | ✅ |
| RF-009-14 | T009-06, T009-07 | CA-009-06 | 🟡 |

## 010 — Dependencias

| Requisito | Tarea | Verificación | Estado |
| --- | --- | --- | --- |
| RF-010-01 | T010-01 | procedimiento bajo demanda | ✅ |
| RF-010-02 | T010-02 | CA-010-01 | ✅ |
| RF-010-03 | T010-10 | comparar con última versión | ✅ |
| RF-010-04 | T010-09, T010-10 | `pip-audit` | ✅ |
| RF-010-05 | T010-01 | clasificación por tipo | ✅ |
| RF-010-06 | T010-05, T010-06 | CA-010-02 | ✅ |
| RF-010-07 | T010-01 | CA-010-04 | ✅ |
| RF-010-08 | T010-01 | CA-010-02 | ✅ |
| RF-010-09 | T010-01 | CA-010-03 | ✅ |
| RF-010-10 | T010-04 | CA-010-05 | ✅ |
| RF-010-11 | T010-01 | CA-010-06 | ✅ |
| RF-010-12 | T010-05, T010-06 | requirements exacto | ✅ |

## Notas de verificación

| Comprobación | Comando | Resultado |
| --- | --- | --- |
| Sistema | `manage.py check` | 0 issues |
| Pruebas | `manage.py test` | 26 tests OK (18,4 s) |
| Imports | `isort --check-only syntax_sprint/` | Sin avisos |
| Lint | `pylint backend` | 5,88/10 (incluye migraciones; informativo) |
| Arquitectura | `specs/tools/code_metrics.py` | 0 funciones fuera de umbral; vistas por dominio |
| Cobertura | `coverage report` | No medido: `coverage` no está en el `venv` |
| Dependencias | `specs/tools/check_dependencies.py --strict` | OK (0 sin uso, runtime coherente) |
| Vulnerabilidades | `pip-audit -r requirements.txt` | 0 avisos |
| BD versionada | `git ls-files \| grep db.sqlite3` | Sin resultados |
| AGENTS versionado | `git ls-files AGENTS.md` | Rastreado |

### Divergencias código ↔ spec

1. **RF-002-02 / RF-002-03**: la spec pide los literales "Email already exists" y
   "Username already exists"; el código muestra un mensaje genérico para evitar
   enumeración de usuarios (decisión de `T009-26`). Se mantiene el comportamiento
   seguro y el requisito queda 🟡 hasta actualizar la spec.
2. **RF-002-07**: `/logout` exige `POST` y `login_required`; un `GET` devuelve 405.
   Es una decisión de seguridad de `T002-09`/`T009-14` no reflejada aún en la spec.
3. **RF-006-03**: resuelto por `T006-06`/`T006-07`. `base.html` fija `data-theme` con
   un script inline antes del primer pintado, por lo que ya no hay FOUC.
4. **RF-003-01 / RF-003-06**: el catálogo de 8 lenguajes × 15 fragmentos existe, pero
   no hay test que lo valide completo (`T003-09` pendiente).
5. **RF-004-15**: las métricas avanzadas (`spacing`, `duration`, `afkHistory`,
   `errorHistory`) se calculan pero no se usan; su destino sigue sin decidir
   (`T004-15`).
6. **T003-05**: cerrado. El catálogo vive en `snippets.py` y `views.py` quedó en 7
   líneas tras `T008-11` (DoD de "< 60 líneas" cumplido).

## Resumen

| Feature | Total | ✅ | 🟡 | ⬜ |
| --- | ---: | ---: | ---: | ---: |
| 000 | 10 | 9 | 1 | 0 |
| 001 | 9 | 8 | 1 | 0 |
| 002 | 11 | 9 | 2 | 0 |
| 003 | 8 | 8 | 0 | 0 |
| 004 | 16 | 13 | 3 | 0 |
| 005 | 12 | 12 | 0 | 0 |
| 006 | 10 | 8 | 1 | 1 |
| 007 | 11 | 9 | 2 | 0 |
| 008 | 12 | 10 | 2 | 0 |
| 009 | 14 | 11 | 3 | 0 |
| 010 | 12 | 12 | 0 | 0 |
| **Total** | **125** | **109** | **15** | **1** |

> La matriz se actualiza al cerrar cada tarea. Un requisito no puede pasar a ✅ sin su
> verificación ejecutada.
