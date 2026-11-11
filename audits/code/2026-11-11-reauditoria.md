# Auditoría de código — Reauditoría 2026-11-11

| Campo | Valor |
| --- | --- |
| Tipo | Código y arquitectura |
| Fecha | 2026-11-11 |
| Auditor | Agente (procedimiento `specs/008-code-audit`) |
| Alcance | `syntax_sprint/` completo |
| Commit auditado | `9572004` + cambios locales de `T008-14`/`T008-15` |
| Herramientas | Python 3.12.1, Django 5.2.19, pylint 4.1.3 + pylint-django 2.8.0, isort 5.13.2, coverage 7.17.2 |
| Resultado global | **8.8 / 10 — B** |

## 1. Alcance y exclusiones

- Incluido: `backend/`, `syntax_sprint/`, `static/js/`, plantillas, CSS y build de Tailwind.
- Excluido: `venv/`, `db.sqlite3`, `__pycache__/`, `staticfiles/`, `node_modules/` e
  historial de git.

## 2. Resumen ejecutivo

La deuda estructural ALTA de la línea base está cerrada: vistas separadas por dominio,
catálogo validado al importar, 39 tests con 99 % de cobertura, `pylint` 10/10, sin líneas
largas propias ni riesgos JS. El perfil usa 5 consultas y el endpoint de fragmentos
responde con p95 de 0.54 ms en local. No hay hallazgos CRÍTICOS, ALTOS ni MEDIOS. Quedan
tres hallazgos BAJOS: el tamaño de `script.js` (482 líneas), las métricas avanzadas sin
usar y la ausencia de tests de frontend.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-101 | BAJA | Módulo grande | `static/js/script.js` | `code_metrics.py --json`: 482 LOC en la auditoría; 404 tras `T004-15` (> 400) | Mantenimiento del motor | Dividir por responsabilidades junto con tests de frontend | M | Abierto |
| AUD-102 | BAJA | Código muerto | `static/js/script.js` | `spacing`, `duration`, `afkHistory`, `errorHistory` se calculaban y no se usaban | Complejidad innecesaria | Eliminarlas (`T004-15`) | S | Resuelto |
| AUD-103 | BAJA | Sin tests de frontend | `static/js/` | No hay runner JS; `manage.py test` solo cubre backend | Regresiones invisibles en el motor | Vitest/jsdom o Playwright (backlog 004) | M | Abierto |
| AUD-104 | INFO | Migración generada | `backend/migrations/0001_initial.py` | 2 líneas > 100 | Ruido de lint | Aceptado: no se editan migraciones aplicadas | — | Aceptado |
| AUD-105 | INFO | Fallback anticipado | `backend/snippets.py` | `CODE_SNIPPETS.get(language, CODE_SNIPPETS["python"])` evalúa el fallback siempre | Ninguno: la validación garantiza `python` | Sin acción | — | Aceptado |

## 4. Métricas

| Métrica | Valor | Umbral | Estado |
| --- | ---: | ---: | --- |
| Archivos analizados | 24 | — | — |
| Líneas de código | 1798 | — | — |
| Funciones | 64 | — | — |
| Funciones fuera de umbral | 0 | 0 | ✅ |
| Función más larga | ≤ 40 | 40 | ✅ |
| Funciones sin anotaciones (sin tests) | 0 | 0 | ✅ |
| Líneas > 100 | 2 (migración) | 0 | ⚠️ aceptado |
| Riesgos JS | 0 | 0 | ✅ |
| Tests | 39 | ≥ 80 % cobertura | ✅ |
| Cobertura `backend/` | 99 % | ≥ 80 % | ✅ |
| Pylint | 10.00/10 | ≥ 8.0 | ✅ |
| isort | 0 avisos | 0 | ✅ |
| Consultas por request en `/profile` | 5 | ≤ 5 | ✅ |
| p95 `/get_python_function` local | 0.54 ms | < 300 ms | ✅ |
| Módulo más grande | `script.js` (482) | ≤ 400 | ❌ |
| Duplicación | No medida | < 3 % | — |

## 5. Puntuación por dimensión

| Dimensión | Peso | Nota | Justificación |
| --- | ---: | ---: | --- |
| D1 Arquitectura | 20 % | 9 | Vistas por dominio, validadores, catálogo separado, middleware CSP y plantilla base |
| D2 Escalabilidad | 20 % | 9 | Paginación, catálogo extensible, configuración por entorno; sin estado global en backend |
| D3 Legibilidad | 15 % | 9 | Sin funciones fuera de umbral ni líneas largas propias; `script.js` grande pero cohesivo |
| D4 Errores | 15 % | 9 | 400/405 correctos, validación defensiva, 500 genérico, CSRF y rate limit |
| D5 Testabilidad | 10 % | 8 | 39 tests y 99 % de cobertura; sin tests de frontend |
| D6 Rendimiento | 10 % | 9 | 5 consultas en perfil y p95 < 1 ms; sin caché explícita |
| D7 Frontend | 5 % | 7 | Sin `innerHTML`, CSP estricta e intervalos limpios; 482 líneas y sin tests |
| D8 Dependencias/docs | 5 % | 9 | Versiones fijadas, `isort` limpio y documentación alineada |
| **Global** | **100 %** | **8.8** | **B** |

Cálculo: 1.8 + 1.8 + 1.35 + 1.35 + 0.8 + 0.9 + 0.35 + 0.45 = **8.85 → 8.8**.

## 6. Comparación con la auditoría anterior

| Métrica | 2026-11-10 | 2026-11-11 | Tendencia |
| --- | ---: | ---: | --- |
| Nota global | 3.8 (F) | 8.8 (B) | +5.0 |
| Hallazgos ALTA | 2 | 0 | ✅ |
| Funciones fuera de umbral | 1 (151 líneas) | 0 | ✅ |
| Líneas > 100 propias | 68 | 0 | ✅ |
| Funciones sin tipos | 9 | 0 | ✅ |
| Tests | 0 | 39 | ✅ |
| Cobertura | No medida | 99 % | ✅ |
| Pylint | 0.69/10 | 10.00/10 | ✅ |
| isort | 5 archivos | 0 | ✅ |
| Riesgos JS | 1 (`innerHTML`) | 0 | ✅ |
| Consultas en perfil | 2 agregaciones sin paginar | 5 (una agregación + paginación) | ✅ |
| Módulo más grande | `views.py` 282 + `script.js` 550 | `script.js` 482 | ⚠️ |

## 7. Acciones inmediatas (≤ 7 días)

1. Ninguna acción crítica ni ALTA pendiente.
2. Cerrar `T004-15` (métricas avanzadas) para eliminar AUD-102.
3. Planificar tests de frontend y división de `script.js` (AUD-101/AUD-103).

## 8. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| AUD-101, AUD-103 | Backlog de `004-typing-engine` (Vitest/Playwright) | `specs/004-typing-engine` |
| AUD-102 | `T004-15` | `specs/004-typing-engine` |
| AUD-104, AUD-105 | Sin acción | — |

## 9. Comandos ejecutados

```bash
python specs/tools/code_metrics.py
python specs/tools/code_metrics.py --json
cd syntax_sprint && python manage.py check
cd syntax_sprint && python manage.py test
cd syntax_sprint && python -m coverage run --source=backend manage.py test
cd syntax_sprint && python -m coverage report
cd syntax_sprint && python -m pylint backend --rcfile=../.pylintrc
isort --check-only syntax_sprint/
```

Salidas clave: `24 archivos`, `1798 LOC`, `64 funciones`, `0` funciones fuera de umbral,
`0` sin tipos; `39 tests OK`; `TOTAL 99 %`; `pylint 10.00/10`; `isort` sin avisos;
`/profile` con 5 consultas; p95 de 0.54 ms en 100 peticiones locales.

## 10. Limitaciones

- `code_metrics.py` no analiza funciones JS; el tamaño de `script.js` se mide por LOC.
- La duplicación no se midió con una herramienta dedicada (`duplicate-code` está
  desactivado en `pylint`).
- La cobertura es de líneas, no de ramas.
- La latencia se midió con el cliente de Django en local, sin red.

## 11. Cierre posterior

- **AUD-102 resuelto** con `T004-15`: se eliminaron las métricas avanzadas
  (`spacing`, `duration`, `keyOverlap`, `afkHistory`, `errorHistory`, `isInError`).
- `script.js` baja de **482 a 404 LOC**; AUD-101 sigue abierto por 4 líneas.
- LOC totales: 1720; los 39 tests siguen en verde y `code_metrics --strict` pasa.
