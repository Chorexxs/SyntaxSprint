# Auditoría de código — Línea base 2026-11-10

| Campo | Valor |
| --- | --- |
| Tipo | Código y arquitectura |
| Fecha | 2026-11-10 |
| Auditor | Agente (procedimiento `specs/008-code-audit`) |
| Alcance | `syntax_sprint/` completo |
| Commit auditado | `d85ff1d` + cambios locales de `specs/` |
| Herramientas | Python 3.12.1, Django 5.2.6, pylint 3.3.4, isort 5.13.2 |
| Resultado global | **3.8 / 10 — F** |

## 1. Alcance y exclusiones

- Incluido: `backend/`, `syntax_sprint/`, `static/js/`, plantillas y CSS.
- Excluido: `venv/`, `db.sqlite3`, `__pycache__/`, historial de git.

## 2. Resumen ejecutivo

El proyecto funciona y `manage.py check` pasa, pero la calidad estructural es baja:
cero pruebas, una función de 151 líneas que mezcla catálogo y HTTP, imports duplicados,
61 líneas largas y un motor JS de 550 líneas sin tests. `pylint` puntúa 0.69/10 e `isort`
falla en 5 archivos. El riesgo principal no es un bug concreto sino la **ausencia de red
de seguridad** para refactorizar.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-001 | ALTA | Función monolítica | `backend/views.py:31` | `code_metrics.py`: 151 líneas | Difícil de mantener y probar | Extraer catálogo y helper | M | Abierto |
| AUD-002 | ALTA | Sin pruebas | `backend/tests.py:1` | `manage.py test`: 0 tests | Regresiones invisibles | Implementar suite (T007-01…04) | M | Abierto |
| AUD-003 | MEDIA | Imports duplicados | `backend/views.py:1-25` | bloques 1–12 y 15–25 repetidos | Confusión y deuda | Un solo bloque ordenado | S | Abierto |
| AUD-004 | MEDIA | Imports sin usar | `backend/views.py:2,6` | `HttpResponse`, `requests` | Ruido | Eliminar | S | Abierto |
| AUD-005 | MEDIA | Líneas largas | `backend/views.py` | 61 líneas > 100 | Legibilidad | Reformatear | S | Abierto |
| AUD-006 | MEDIA | Líneas largas JS | `static/js/script.js` | 7 líneas > 100 | Legibilidad | Reformatear | S | Abierto |
| AUD-007 | MEDIA | isort | 5 archivos | `isort --check-only` falla | Imports inconsistentes | Ejecutar isort + CI | S | Abierto |
| AUD-008 | MEDIA | Pylint | repo | 0.69/10 | Deuda generalizada | Cargar plugin Django y corregir | M | Abierto |
| AUD-009 | MEDIA | Sin tipos | 9 funciones | `code_metrics.py`: 9/9 sin tipar | Menos claridad | Anotar firmas | S | Abierto |
| AUD-010 | MEDIA | XSS potencial | `static/js/script.js:201` | `innerHTML = letters` | Inyección si el contenido no es confiable | Usar nodos/`textContent` | S | Abierto |
| AUD-011 | MEDIA | Módulo grande | `backend/views.py` | 282 líneas | Baja cohesión | Separar `snippets.py` y servicios | M | Abierto |
| AUD-012 | BAJA | Líneas largas generadas | `migrations/0001_initial.py` | 2 líneas > 100 | Ruido | Ignorar migraciones en lint | S | Aceptado |
| AUD-013 | BAJA | Tema duplicado | 4 plantillas | header y toggle repetidos | Cambios inconsistentes | `base.html` + `theme.js` | M | Abierto |
| AUD-014 | BAJA | Métricas muertas | `script.js` | `spacing`, `duration`, `afkHistory` sin uso | Complejidad innecesaria | Usar o eliminar | S | Abierto |
| AUD-015 | INFO | Check de Django | repo | `manage.py check` OK | — | Mantener | — | ✅ |

## 4. Métricas

| Métrica | Valor | Umbral | Estado |
| --- | ---: | ---: | --- |
| Archivos analizados | 16 | — | — |
| Líneas de código | 919 | — | — |
| Funciones | 9 | — | — |
| Función más larga | 151 | 40 | ❌ |
| Funciones sin tipos | 9 | 0 en código nuevo | ❌ |
| `views.py` líneas > 100 | 61 | 0 | ❌ |
| `script.js` líneas > 100 | 7 | 0 | ❌ |
| Riesgos JS | 1 | 0 | ⚠️ |
| `except` desnudo | 0 | 0 | ✅ |
| `print()` reales | 0 | 0 | ✅ |
| Tests | 0 | ≥ 80 % cobertura | ❌ |
| Pylint | 0.69 | ≥ 8.0 | ❌ |
| isort | 5 archivos | 0 | ❌ |

## 5. Puntuación por dimensión

| Dimensión | Peso | Nota | Justificación |
| --- | ---: | ---: | --- |
| D1 Arquitectura | 20 % | 4 | Vista monolítica, catálogo embebido |
| D2 Escalabilidad | 20 % | 4 | Sin paginación, configuración mezclada, catálogo acoplado |
| D3 Legibilidad | 15 % | 4 | 151 líneas, duplicación, 61 líneas largas |
| D4 Errores | 15 % | 3 | Sin `try/except` en JSON, `KeyError`, guardado silencioso |
| D5 Testabilidad | 10 % | 2 | Cero pruebas |
| D6 Rendimiento | 10 % | 5 | SQLite y 2 agregaciones; sin caché |
| D7 Frontend | 5 % | 5 | Clase de 550 líneas, `innerHTML`, sin tests |
| D8 Dependencias/docs | 5 % | 4 | isort falla, README desalineado |
| **Global** | **100 %** | **3.8** | **F** |

## 6. Acciones inmediatas (≤ 7 días)

1. Crear la suite de pruebas (`T007-01`…`T007-04`).
2. Extraer el catálogo a `backend/snippets.py` (`T003-05`).
3. Eliminar imports duplicados y sin usar (`T001-09`).
4. Ejecutar `isort` y añadirlo a CI (`T007-13`).
5. Reemplazar `innerHTML` (`T008-12`).

## 7. Tareas creadas

| Hallazgo | Tarea |
| --- | --- |
| AUD-001, AUD-011 | T008-06, T008-11, T003-05 |
| AUD-002 | T008-13, T007-01…04 |
| AUD-003, AUD-004 | T008-07, T001-09 |
| AUD-005, AUD-006 | T008-09 |
| AUD-007 | T008-08 |
| AUD-009 | T008-10 |
| AUD-010 | T008-12 |
| AUD-013 | T006-05, T006-06 |
| AUD-014 | T004-15 |

## 8. Comandos ejecutados

```bash
python specs/tools/code_metrics.py
isort --check-only syntax_sprint
python -m pylint syntax_sprint/backend syntax_sprint/syntax_sprint --score=y
cd syntax_sprint && python manage.py check
cd syntax_sprint && python manage.py test
```

## 9. Limitaciones

- `code_metrics.py` aproxima complejidad con `ast` y cuenta funciones anidadas por
  separado; se contrasta con `pylint`.
- No se midió duplicación exacta ni cobertura (no hay tests).
- La revisión manual D1–D8 está parcialmente cubierta por esta línea base.
