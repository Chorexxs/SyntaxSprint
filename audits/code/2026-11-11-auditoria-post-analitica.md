# Auditoría de código — 2026-11-11 (post-analítica)

| Campo | Valor |
| --- | --- |
| Tipo | Código y arquitectura (spec 008) |
| Fecha | 2026-11-11 |
| Auditor | Agente (OpenCode) |
| Alcance | Repo completo: `backend/`, `syntax_sprint/`, JS, plantillas y documentación |
| Commit auditado | `8e39fc0` (`main`) |
| Herramientas | `code_metrics.py`, `pylint`, `isort`, `coverage`, `manage.py check`, `manage.py test` |
| Resultado global | **8.55/10 (B)** · sin hallazgos ALTA |

## 1. Alcance y exclusiones

- Incluido: código Python de `backend/` y `syntax_sprint/`, `static/js/*.js`, plantillas,
  estilos y documentación de `specs/`.
- Excluido: `venv/`, `node_modules/`, `db.sqlite3`, migraciones autogeneradas (solo se
  miden, no se penalizan), CVEs (ver informe de seguridad) e historial de git.

## 2. Resumen ejecutivo

La base sigue sana: 94 funciones, ninguna fuera de los umbrales de longitud, complejidad,
anidamiento o parámetros; `pylint` 10.00/10, `isort` sin avisos, `code_metrics --strict`
sin incumplimientos y 52 tests con 99 % de cobertura. Las vistas están separadas por
dominio y la nueva lógica de analítica vive en su propio módulo.

La nota baja ligeramente de 8.8 a 8.55 por la nueva superficie de analítica: una escritura
por petición sin purga programada y un helper con nombre engañoso. No hay duplicación
relevante, código muerto ni funciones largas.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-013 | BAJA | D8 Documentación | `static/js/theme.js:4` | El comentario dice que `data-theme` lo fija un script **inline** en `base.html`; `base.html:12` carga `theme-init.js` | Confunde al siguiente mantenedor y contradice la CSP sin `unsafe-inline` | Corregir el comentario | S | Abierto |
| AUD-014 | BAJA | D4 Errores / observabilidad | `syntax_sprint/settings.py` (sin `LOGGING`), `backend/analytics.py:16` | Django usa el logging por defecto a stderr; sin formato, nivel ni destino configurables. `logger.exception` de analítica depende de ese default | Diagnóstico lento en producción y sin control de retención | Añadir `LOGGING` con formato, nivel y un handler de consola | S | Abierto |
| AUD-015 | BAJA | D3 Legibilidad / D2 | `backend/auth_views.py:81-83` | `_client_ip()` devuelve `REMOTE_ADDR` y se usa como clave del rate limit | Nombre engañoso: sugiere IP de cliente cuando puede ser la del proxy (ver SEC-016) | Renombrar a `_request_ip` o resolver la IP real | S | Abierto |
| AUD-016 | INFO | D6 Rendimiento | `backend/analytics.py:71-80` | `build_report` recalcula el inicio de ventana en cada métrica | Impacto despreciable (4 cálculos) | Pasar un único `since` si se amplía el informe | S | Abierto |

> Cada hallazgo incluye ubicación y evidencia. Los umbrales objetivos se cumplen todos.

## 4. Métricas

| Métrica | Valor | Umbral | Estado |
| --- | --- | --- | --- |
| Archivos analizados | 30 | — | — |
| Líneas de código (Python/JS) | 2006 | — | — |
| Funciones | 94 | — | — |
| Funciones > 40 líneas | 0 | 0 | ✅ |
| Complejidad > 10 | 0 | 0 | ✅ |
| Anidamiento > 4 | 0 | 0 | ✅ |
| Parámetros > 5 | 0 | 0 | ✅ |
| Funciones sin anotaciones (sin tests) | 0 | 0 | ✅ |
| `except` desnudo / `except Exception` | 0 | 0 | ✅ |
| `print()` en producción | 0 | 0 | ✅ |
| Líneas > 100 (código) | 0 | 0 | ✅ |
| Líneas > 100 en migraciones | 3 | autogeneradas | ✅ |
| Tests | 52 | — | ✅ |
| Cobertura | 99 % (651 sentencias, 6 sin cubrir) | ≥ 80 % | ✅ |
| Pylint | 10.00/10 | ≥ 8.0 | ✅ |
| isort | Sin avisos | 0 | ✅ |
| `manage.py check` | 0 issues | 0 | ✅ |
| `code_metrics --strict` | Sin incumplimientos | 0 | ✅ |
| p95 endpoint de fragmentos (local) | 6,11 ms | < 300 ms | ✅ |
| Consultas del perfil | ≤ 5 (test) | ≤ 5 | ✅ |
| Riesgos JS (`innerHTML`, `eval`, `var`, `==`) | 0 | 0 | ✅ |

### Puntuación por dimensión

| Dimensión | Peso | Nota | Justificación |
| --- | ---: | ---: | --- |
| D1 Arquitectura | 20 % | 9 | Vistas por dominio, catálogo aislado, `analytics.py` propio, plantillas sin lógica |
| D2 Escalabilidad | 20 % | 8 | Paginación e índices correctos; analítica con purga manual y caché de rate limit por proceso |
| D3 Legibilidad | 15 % | 9 | Sin funciones largas ni duplicación; un comentario y un helper engañosos |
| D4 Errores | 15 % | 9 | 400/405 correctos, JSON defensivo, `fail-open` acotado a `DatabaseError`; falta configurar `LOGGING` |
| D5 Testabilidad | 10 % | 8 | 99 % de cobertura y funciones puras; sin tests de frontend |
| D6 Rendimiento | 10 % | 8 | p95 6 ms local, ≤ 5 consultas en perfil; agregaciones sobre tabla creciente |
| D7 Frontend | 5 % | 8 | Sin `innerHTML`/`eval`, intervalos limpiados; sin tests automatizados |
| D8 Dependencias y docs | 5 % | 9 | Versiones fijadas, `pip-audit` limpio, docs alineadas; un comentario obsoleto |

**Cálculo:** 0,20·9 + 0,20·8 + 0,15·9 + 0,15·9 + 0,10·8 + 0,10·8 + 0,05·8 + 0,05·9 =
**8,55 → B**.

## 5. Comparación con la auditoría anterior

| Métrica | 2026-11-11 (reauditoría) | Actual | Tendencia |
| --- | --- | --- | --- |
| Nota global | 8,8 (B) | 8,55 (B) | ▼ leve |
| Archivos | 26 | 30 | ▲ |
| Líneas de código | 919 (base) | 2006 | ▲ (incluye tests y JS) |
| Funciones | 9 (base) | 94 | ▲ |
| Hallazgos ALTA | 0 | 0 | = |
| Tests | 39 | 52 | ▲ |
| Cobertura | 99 % | 99 % | = |
| Pylint | 10.00/10 | 10.00/10 | = |

## 6. Acciones inmediatas (≤ 24 h)

1. Ninguna bloqueante. AUD-013…AUD-015 son de bajo impacto y caben en el próximo ciclo.

## 7. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| AUD-013 | T008-18 | `specs/008-code-audit` |
| AUD-014 | T008-19 | `specs/008-code-audit` |
| AUD-015 | T008-20 | `specs/008-code-audit` |
| AUD-016 | — (INFO) | — |

## 8. Comandos ejecutados

```bash
python specs/tools/code_metrics.py
python specs/tools/code_metrics.py --strict
cd syntax_sprint && python manage.py check
cd syntax_sprint && python manage.py test
python -m coverage run --source=backend manage.py test
python -m coverage report --skip-covered
python -m isort --check-only --diff syntax_sprint/
cd syntax_sprint && python -m pylint backend --rcfile=../.pylintrc
manage.py shell            # sonda de latencia del endpoint
```

## 9. Limitaciones

- La latencia se midió en local con SQLite y el cliente de pruebas, no contra producción.
- No hay tests automatizados de frontend (backlog de 004).
- La puntuación de dimensiones es una rúbrica fija, comparable entre ejecuciones, no una
  medida física.
- La auditoría es de solo lectura: los hallazgos no se corrigen aquí.
