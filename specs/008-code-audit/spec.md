# Spec 008 — Auditoría de código y arquitectura

| Campo | Valor |
| --- | --- |
| Estado | Implementada (procedimiento listo) |
| Versión | 1.0 |
| Depende de | 000-overview, 007-quality-and-delivery |
| Archivos principales | `specs/tools/code_metrics.py`, `specs/templates/audit-report.md` |
| Disparadores | "audita el código", "auditoría de código", "revisa la calidad", "revisa la arquitectura" |

## 1. Contexto y problema

El proyecto creció rápido y ya presenta señales de código espagueti: una función de 151
líneas, imports duplicados, cero pruebas y un archivo `views.py` que mezcla catálogo,
HTTP y lógica de negocio. Sin un procedimiento repetible, la calidad depende de la
memoria y cada revisión descubre cosas distintas.

Este spec define **cómo auditar el código cuando el usuario lo indique**, con criterios
objetivos, evidencia verificable y un informe comparable entre ejecuciones.

## 2. Objetivos

1. Detectar errores, deuda técnica y malas prácticas de forma sistemática.
2. Evaluar arquitectura, modularidad y escalabilidad, no solo estilo.
3. Producir un informe reproducible con severidad e impacto.
4. Convertir cada hallazgo en una tarea o spec accionable.
5. Medir tendencia entre auditorías.

### No objetivos

- Corregir el código durante la auditoría (es de solo lectura).
- Sustituir la auditoría de seguridad (ver `009-cybersecurity`).
- Pruebas de carga o profiling profundo (backlog).
- Revisar dependencias de terceros por CVE (ver 009).

## 3. Cuándo se ejecuta

La auditoría se activa **solo** cuando el usuario lo pide explícitamente, con frases como:

- "audita el código"
- "haz una auditoría de código"
- "revisa la calidad / la arquitectura / la escalabilidad"
- "¿esto es código espagueti?"

Si no hay disparador, no se ejecuta. No se audita automáticamente en cada cambio.

## 4. Alcance

| Incluido | Excluido |
| --- | --- |
| `syntax_sprint/backend/**/*.py` | `venv/` |
| `syntax_sprint/syntax_sprint/*.py` | `db.sqlite3` |
| `syntax_sprint/static/js/*.js` | `__pycache__/`, `*.pyc` |
| `syntax_sprint/static/css/*.css` | Archivos generados por Django |
| `syntax_sprint/templates/*.html` | Dependencias de terceros |
| `specs/` y documentación | Historial de git (ver 009) |

El usuario puede limitar el alcance a una ruta: "audita `backend/views.py`".

## 5. Dimensiones y pesos

| # | Dimensión | Peso | Qué evalúa |
| --- | --- | --- | --- |
| D1 | Arquitectura y modularidad | 20 % | Capas, cohesión, acoplamiento, responsabilidades |
| D2 | Escalabilidad | 20 % | Crecimiento, configuración, consultas, paginación, extensibilidad |
| D3 | Legibilidad y mantenibilidad | 15 % | Nombres, duplicación, longitud, anidamiento, magia |
| D4 | Manejo de errores y validación | 15 % | Excepciones, 400/500, entradas, degradación |
| D5 | Testabilidad y cobertura | 10 % | Tests, funciones puras, dependencias inyectables |
| D6 | Rendimiento | 10 % | Consultas, N+1, caché, payloads, tiempos |
| D7 | Frontend | 5 % | Estado, DOM, listeners, XSS, tamaño |
| D8 | Dependencias y documentación | 5 % | Versiones, imports, docs alineadas |

Cada dimensión se puntúa de **0 a 10** con la evidencia recogida.

## 6. Umbrales objetivos

| Métrica | Umbral | Herramienta |
| --- | --- | --- |
| Longitud de función | ≤ 40 líneas | `code_metrics.py` |
| Complejidad ciclomática | ≤ 10 | `code_metrics.py` / `pylint` |
| Anidamiento | ≤ 4 niveles | `code_metrics.py` |
| Parámetros por función | ≤ 5 | `code_metrics.py` |
| Longitud de línea | ≤ 100 caracteres | `pylint` |
| Longitud de módulo | ≤ 400 líneas | `code_metrics.py` |
| Funciones sin anotaciones | 0 en código nuevo | `code_metrics.py` |
| `except` desnudo | 0 | `code_metrics.py` |
| `print()` en producción | 0 (usar `logging`) | `code_metrics.py` |
| Cobertura de pruebas | ≥ 80 % | `coverage` |
| Duplicación | < 3 % | `pylint` / revisión |
| Consultas por request (perfil) | ≤ 5 | `connection.queries` |
| p95 endpoint fragmentos | < 300 ms | medición manual |
| Imports desordenados | 0 | `isort` |
| Pylint | ≥ 8.0/10 | `pylint` |

Un umbral incumplido genera hallazgo, pero la severidad depende del impacto, no solo del
número.

## 7. Severidad

| Severidad | Criterio | SLA |
| --- | --- | --- |
| CRÍTICA | Rompe producción, corrupción de datos o bloquea el crecimiento | ≤ 24 h |
| ALTA | Deuda estructural grave, error frecuente, sin pruebas en ruta crítica | ≤ 7 días |
| MEDIA | Mal práctica localizada, duplicación relevante, error de borde | ≤ 30 días |
| BAJA | Estilo, nombres, código muerto menor | ≤ 90 días |
| INFO | Observación o control positivo | Sin acción |

## 8. Procedimiento

### Paso 0 — Preparación (2 min)

```bash
git status --short
git rev-parse --short HEAD
```

Registrar commit auditado. Si hay cambios sin commitear, auditar el working tree y
anotarlo en el informe.

### Paso 1 — Automático (5 min)

```bash
python specs/tools/code_metrics.py
cd syntax_sprint && python manage.py check
cd syntax_sprint && python manage.py test
isort --check-only syntax_sprint/
pylint syntax_sprint/backend syntax_sprint/syntax_sprint --score=y
```

Registrar salida y versión de las herramientas. Si `manage.py test` no tiene tests, es
un hallazgo ALTA por sí mismo.

### Paso 2 — Revisión manual por dimensión (10 min)

**D1 Arquitectura**
- ¿Las vistas solo orquestan HTTP o contienen negocio?
- ¿Hay capas claras (vista → servicio/helper → modelo)?
- ¿El catálogo de snippets está separado de la vista?
- ¿Las plantillas contienen lógica que debería estar en el backend?

**D2 Escalabilidad**
- ¿Añadir un lenguaje obliga a editar la vista?
- ¿Añadir un modo de test duplica el motor?
- ¿El historial crece sin paginación?
- ¿La configuración depende del entorno o está hardcodeada?
- ¿Hay estado global o en memoria que impida escalar horizontalmente?

**D3 Legibilidad**
- Funciones > 40 líneas, anidamiento > 4, nombres ambiguos.
- Duplicación de bloques (header, tema, fórmulas).
- Números mágicos sin constante.
- Código muerto e imports sin usar.

**D4 Errores**
- ¿Todo `json.loads` tiene `try/except`?
- ¿Los accesos a `request.POST` son defensivos?
- ¿Los endpoints devuelven 400/405 correctos?
- ¿Los fallos de red se comunican al usuario?
- ¿Hay `except: pass` o `except Exception` genéricos?

**D5 Testabilidad**
- ¿Hay tests? ¿Cubren caminos de error?
- ¿Las funciones puras se pueden probar sin Django?
- ¿Las dependencias están acopladas a globales?

**D6 Rendimiento**
- N+1 queries, agregaciones repetidas, `len(queryset)` innecesario.
- Falta de índices en campos filtrados/ordenados.
- Payloads grandes, assets sin caché.

**D7 Frontend**
- Funciones > 40 líneas, estado global mutable.
- `innerHTML` con datos no confiables.
- Listeners o intervalos que no se limpian.
- `var`, `==`, `eval`, `document.write`.

**D8 Dependencias y docs**
- Versiones fijadas y coherentes.
- Imports ordenados.
- README/specs alineados con el código.

### Paso 3 — Clasificar y puntuar (3 min)

1. Asignar severidad a cada hallazgo.
2. Puntuar cada dimensión (0–10) justificando con evidencia.
3. Calcular la nota global:

```text
Score = Σ (puntuación_dimensión × peso)
```

| Nota | Rango |
| --- | --- |
| A | 9.0 – 10 |
| B | 8.0 – 8.9 |
| C | 7.0 – 7.9 |
| D | 6.0 – 6.9 |
| F | < 6.0 |

### Paso 4 — Informe (5 min)

Crear `audits/code/AAAA-MM-DD-<alcance>.md` usando
`specs/templates/audit-report.md`. Cada hallazgo debe tener:

- ID `AUD-NNN`
- Severidad
- Ubicación `archivo:línea`
- Evidencia (comando + salida o fragmento mínimo)
- Impacto
- Recomendación concreta
- Esfuerzo (S/M/L)
- Tarea o spec propuesta

### Paso 5 — Cierre

- Añadir las tareas a `tasks.md` de la funcionalidad correspondiente o crear un spec
  nuevo si el cambio es grande.
- Actualizar `specs/traceability.md` si cambia el alcance.
- Comparar con la auditoría anterior si existe.

## 9. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-008-01 | Cuando el usuario use un disparador, el sistema debe ejecutar el procedimiento completo. | Alta |
| RF-008-02 | La auditoría debe respetar el alcance indicado (repo o ruta). | Alta |
| RF-008-03 | El informe debe cubrir las 8 dimensiones con puntuación. | Alta |
| RF-008-04 | Cada hallazgo debe incluir ubicación `archivo:línea` y evidencia reproducible. | Alta |
| RF-008-05 | La auditoría debe clasificar hallazgos por severidad y SLA. | Alta |
| RF-008-06 | El informe debe calcular una nota global reproducible. | Media |
| RF-008-07 | La auditoría debe ser de solo lectura: no modifica código. | Alta |
| RF-008-08 | Cada hallazgo debe convertirse en tarea o spec. | Alta |
| RF-008-09 | El informe debe guardarse en `audits/code/`. | Media |
| RF-008-10 | Debe existir una línea base medible para comparar. | Media |
| RF-008-11 | La auditoría debe detectar código espagueti (funciones largas, duplicación, acoplamiento). | Alta |
| RF-008-12 | La auditoría debe evaluar escalabilidad y extensibilidad, no solo estilo. | Alta |

## 10. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-008-01 | El procedimiento completo debe tardar < 20 minutos en este repositorio. |
| RNF-008-02 | Los comandos deben ser deterministas y no requerir red. |
| RNF-008-03 | El informe se escribe en español. |
| RNF-008-04 | Los falsos positivos deben marcarse explícitamente. |
| RNF-008-05 | No se imprime ni se guarda ningún secreto (ver 009). |

## 11. Criterios de aceptación

- **CA-008-01** Dado el disparador "audita el código", cuando termina, existe un informe en `audits/code/` con las 9 secciones de la plantilla.
- **CA-008-02** Cada hallazgo tiene `archivo:línea` y comando o fragmento reproducible.
- **CA-008-03** Las 8 dimensiones tienen puntuación y la nota global se puede recalcular.
- **CA-008-04** La auditoría no deja cambios en `git status` salvo el propio informe.
- **CA-008-05** Cada hallazgo ALTA o superior tiene tarea o spec asociada.
- **CA-008-06** `code_metrics.py` detecta funciones > 40 líneas, complejidad > 10 y anidamiento > 4.

## 12. Línea base medida — 2026-11-10

| Métrica | Valor | Umbral | Estado |
| --- | --- | ---: | --- |
| Archivos analizados | 16 | — | — |
| Líneas de código (Python/JS) | 919 | — | — |
| Funciones | 9 | — | — |
| Función más larga | `get_python_function` (151 líneas) | 40 | ❌ |
| Funciones sin anotaciones | 9 de 9 | 0 en código nuevo | ❌ |
| Líneas > 100 en `views.py` | 61 | 0 | ❌ |
| Líneas > 100 en `script.js` | 7 | 0 | ❌ |
| `innerHTML` en JS | 1 (`script.js:201`) | 0 con datos no confiables | ⚠️ |
| Tests | 0 | ≥ 80 % cobertura | ❌ |
| Pylint | 0.69/10 | ≥ 8.0 | ❌ |
| isort | 5 archivos fallan | 0 | ❌ |
| `manage.py check` | 0 issues | 0 | ✅ |
| `except` desnudo | 0 | 0 | ✅ |

**Nota preliminar:** 3.8/10 (F). No sustituye la auditoría completa; sirve de referencia.

> Reauditoría del 2026-11-11: `audits/code/2026-11-11-reauditoria.md` → **8.8/10 (B)**,
> 0 hallazgos ALTA.
>
> Reauditoría del 2026-11-12 tras cerrar la Fase 6:
> `audits/code/2026-11-12-reauditoria.md` → **8.9/10 (B)**, 0 ALTA; 1 MEDIA de tooling,
> 1 BAJA y 1 INFO.
>
> Reauditoría post-analítica del 2026-11-11:
> `audits/code/2026-11-11-auditoria-post-analitica.md` → **8.55/10 (B)**, 0 ALTA y
> 4 hallazgos menores (AUD-013…AUD-016).
>
> Remediación del 2026-11-11: AUD-013, AUD-014 y AUD-015 cerrados (`T008-18`…`T008-20`);
> AUD-016 (INFO) queda en `T008-21`.
>
> Auditoría post-2FA del 2026-11-11:
> `audits/code/2026-11-11-auditoria-post-2fa.md` → **8.25/10 (B)**, 0 ALTA, 2 MEDIA
> (AUD-017, AUD-018) y 8 BAJAS (AUD-019…AUD-026), con tareas `T008-22`…`T008-31`.

## 13. Fuera de alcance

- Corrección de los hallazgos.
- Auditoría de seguridad y secretos (spec 009).
- Análisis de CVE de dependencias.
- Pruebas de carga.

## 14. Riesgos

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Auditar sin tests y confundir comportamiento con bug | Falsos positivos | Marcar supuestos; validar en runtime |
| Puntuación subjetiva | Informes incomparables | Umbrales y rúbrica fijos |
| Informe enorme e inaccionable | Se ignora | Máximo 15 hallazgos, priorizados |
| Auditoría que se convierte en refactor | Pierde objetividad | Regla de solo lectura |

## 15. Referencias

- `specs/tools/code_metrics.py`
- `specs/templates/audit-report.md`
- `audits/code/2026-11-10-linea-base.md`
- `specs/000-overview/plan.md` (ADRs y deuda transversal)
