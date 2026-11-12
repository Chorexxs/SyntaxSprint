# Auditoría de código — 2026-11-12 (arquitectura y espagueti)

| Campo | Valor |
| --- | --- |
| Tipo | Código y arquitectura (spec 008) |
| Fecha | 2026-11-12 |
| Auditor | Agente (OpenCode) |
| Alcance | Repo completo; foco en arquitectura, duplicación y tamaño de unidades |
| Commit auditado | `9fb738c` (`main`) |
| Herramientas | `code_metrics.py`, `pylint` 4.1.3, `isort`, `coverage` 7.17.2, `manage.py check/test`, `npm audit`, Vitest 4.1.12, Node 26.13.0 |
| Resultado global | **8.6/10 (B)** · 0 CRÍTICOS, 0 ALTOS, 2 MEDIOS, 2 BAJAS y 1 INFO |

## 1. Alcance y exclusiones

- Incluido: `syntax_sprint/backend/` (vistas por dominio, servicios, comandos,
  middleware, tests), `syntax_sprint/`, plantillas, `static/js`, `tests/js`,
  migraciones y documentación de `specs/`.
- Excluido: `venv/`, `node_modules/`, CVEs de producción (spec 010), pentesting
  (spec 009), historial de git. No se mide duplicación con `jscpd` ni Core Web
  Vitals: quedan en el backlog de 008.

## 2. Resumen ejecutivo

La arquitectura del backend está saneada: las vistas solo orquestan HTTP, la lógica vive
en módulos por dominio (`snippets`, `analytics`, `ratelimit`, `totp`, `two_factor`,
`validators`) y no hay funciones Python fuera de umbral. `code_metrics --strict` está en
verde, `pylint` en 10.00, la cobertura en 97 % y `npm audit` sin avisos.

El único foco de espagueti está en el **frontend**: `script.js` concentra 559 líneas en
una sola clase, con `handleKeydown` (71 líneas) y `startTest` (52) por encima del umbral
de 40, y el mismo bloque de sincronización repetido en cinco manejadores. Además,
`tests.py` supera las 970 líneas. No hay errores funcionales conocidos ni acoplamiento
grave; son mejoras de mantenibilidad, no bloqueantes.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-030 | MEDIA | Arquitectura frontend | `static/js/script.js:103-154, 255-325` | `handleKeydown` 71 líneas y `startTest` 52; archivo de 559 líneas | Clase con demasiadas responsabilidades; difícil de probar y extender | Extraer ayudantes de teclado (`handleBackspace`, `handleNavigation`, `handleTab`) y separar timer/render/guardado en módulos | M | Abierto |
| AUD-031 | MEDIA | Duplicación | `script.js:222-227, 345-350, 364-369, 388-393, 407-412` | El bloque `countTypedChars` + `updateDisplay` + `updateLiveStats` + fin se repite 5 veces | Un cambio en el recuento obliga a tocar cinco sitios | Extraer `syncTypedValue(value)` y reutilizarlo | S | Abierto |
| AUD-032 | BAJA | Tests | `backend/tests.py:1-971` | 971 líneas y 8 clases (`AuthTests`, `SnippetTests`, `ResultTests`, `ProfileTests`, `SecurityHeadersTests`, `CsrfTests`, `AnalyticsTests`, `TwoFactorTests`) | Umbral de módulo (400) superado; navegación y revisión más lentas | Repartir por dominio en `tests_auth.py`, `tests_snippets.py`, etc., siguiendo `tests_ratelimit.py` y `tests_totp.py` | M | Abierto |
| AUD-033 | BAJA | Manejo de errores | `script.js:151-153` | `startTest` solo hace `console.error` si falla el fetch | El usuario no sabe por qué no arranca el test | Mostrar un aviso en el área de test y permitir reintentar | S | Abierto |
| AUD-034 | INFO | Documentación | `syntax_sprint/urls.py:1-16` | Docstring de plantilla de Django sin adaptar | Ruido menor en un archivo de configuración | Sustituirlo por una descripción del enrutado real | S | Abierto |

> Sin secretos ni datos personales en este informe.

### Falsos positivos declarados (RNF-008-04)

| Señal | Motivo |
| --- | --- |
| 5 líneas > 100 en `backend/migrations/0001…0003` | Migraciones autogeneradas; excluidas por `T008-09`. |
| Umbral de módulo en `snippets.py` (350) | Es un catálogo de datos; está por debajo de 400. |

## 4. Métricas

| Métrica | Valor | Umbral | Estado |
| --- | --- | --- | --- |
| Archivos analizados | 38 | — | — |
| Líneas de código Python/JS | 2945 | — | — |
| Funciones Python | 163 | — | — |
| Funciones Python > 40 líneas | 0 | 0 | ✅ |
| Funciones JS > 40 líneas | 2 (`handleKeydown` 71, `startTest` 52) | 0 | ⚠️ AUD-030 |
| Complejidad Python > 10 / anidamiento > 4 | 0 | 0 | ✅ |
| Funciones sin anotaciones | 0 | 0 | ✅ |
| `except` desnudo / `except Exception` | 0 | 0 | ✅ |
| `print()` en producción | 0 | 0 | ✅ |
| `script.js` | 559 líneas | ≤ 400 | ⚠️ AUD-030 |
| `tests.py` | 971 líneas | ≤ 400 | ⚠️ AUD-032 |
| Tests Django | 88 (87 OK + 1 omitido en Windows) | — | ✅ |
| Tests JS | 21 | — | ✅ |
| Cobertura backend | 97 % (1207 sentencias, 32 sin cubrir) | ≥ 80 % | ✅ |
| Pylint | 10.00/10 | ≥ 8.0 | ✅ |
| isort | Sin avisos | 0 | ✅ |
| `manage.py check` | 0 issues | 0 | ✅ |
| `npm audit` | 0 avisos | 0 | ✅ |
| Duplicación medida (`jscpd`) | No medida (manual: 5 bloques) | < 3 % | ⚠️ backlog |

### Puntuación por dimensión

| Dimensión | Peso | Nota | Justificación |
| --- | ---: | ---: | --- |
| D1 Arquitectura | 20 % | 8,5 | Backend por dominios y helpers claros; el frontend es una clase monolítica |
| D2 Escalabilidad | 20 % | 9 | Catálogo de datos, alias de caché configurables, paginación e índices |
| D3 Legibilidad | 15 % | 8 | Duplicación de sincronización, métodos largos y `tests.py` de 971 líneas |
| D4 Errores | 15 % | 8,5 | `fail-open` y validación sólidos; arranque sin aviso al usuario |
| D5 Testabilidad | 10 % | 9 | 109 tests, 97 % de cobertura; el motor JS mezcla DOM y lógica |
| D6 Rendimiento | 10 % | 9 | Sin escrituras extra en fragmentos, ventana única y perfil ≤ 5 consultas |
| D7 Frontend | 5 % | 8 | Sin `innerHTML`/`eval`; monolitio, métodos largos y duplicación |
| D8 Dependencias y docs | 5 % | 9 | Versiones fijadas, 0 CVEs y documentación alineada |

**Cálculo:** 0,20·8,5 + 0,20·9 + 0,15·8 + 0,15·8,5 + 0,10·9 + 0,10·9 + 0,05·8 +
0,05·9 = **8.6 → B**.

## 5. Comparación con la auditoría anterior

| Métrica | Reauditoría (2026-11-12, `805d534`) | Actual (`9fb738c`) | Tendencia |
| --- | --- | --- | --- |
| Nota global | 8.9 (B) | 8.6 (B) | ▼ por el foco en frontend |
| Archivos | 38 | 38 | = |
| Líneas | 2873 | 2945 | ▲ |
| Funciones Python | 159 | 163 | ▲ |
| Tests | 88 + 14 | 88 + 21 | ▲ |
| Cobertura | 97 % | 97 % | = |
| Hallazgos ALTA / MEDIA / BAJA | 0 / 0 / 0 | 0 / 2 / 2 | ▲ (nuevo foco) |

La bajada es de alcance, no una regresión funcional: la auditoría anterior miraba el
cierre de la Fase 6; esta revisa explícitamente arquitectura y tamaño de unidades.

## 6. Acciones inmediatas (≤ 24 h)

1. Ninguna bloqueante: no hay hallazgos CRÍTICOS ni ALTOS.
2. Los MEDIA (`AUD-030`, `AUD-031`) tienen SLA de 30 días; se pueden agrupar en un
   único refactor del motor JS.

## 7. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| AUD-030 | `T004-24` | `specs/004-typing-engine` |
| AUD-031 | `T004-25` | `specs/004-typing-engine` |
| AUD-033 | `T004-26` | `specs/004-typing-engine` |
| AUD-032 | `T007-23` | `specs/007-quality-and-delivery` |
| AUD-034 | — (INFO, sin acción) | — |

## 8. Comandos ejecutados

```bash
git status --short && git rev-parse --short HEAD
# 9fb738c; árbol limpio
python specs/tools/code_metrics.py --strict
# 38 archivos, 2945 líneas, 163 funciones; gate sin incumplimientos
cd syntax_sprint && python manage.py check
# System check identified no issues (0 silenced).
cd syntax_sprint && python manage.py test
# Ran 88 tests; OK (1 omitido en Windows por permisos POSIX)
cd syntax_sprint && coverage run --source=backend manage.py test && coverage report
# TOTAL 1207 sentencias, 32 sin cubrir, 97 %
isort --check-only syntax_sprint/
# Sin avisos
pylint syntax_sprint/backend syntax_sprint/syntax_sprint --score=y
# 10.00/10
python specs/tools/check_dependencies.py --strict
# OK
npm audit
# found 0 vulnerabilities
npm run test:js
# 21 tests OK (Vitest 4.1.12 + jsdom)
node -e "…"  # longitudes de métodos JS: handleKeydown 71, startTest 52
```

Versiones: Python 3.12.1, pylint 4.1.3, coverage 7.17.2, Node 26.13.0, npm 12.2.2,
Vitest 4.1.12.

## 9. Limitaciones

- No se mide duplicación con `jscpd`; la duplicación de AUD-031 se localizó por revisión
  manual.
- La cobertura es de líneas, no de ramas; `ratelimit.py` sigue por debajo por sus ramas
  de degradación.
- Un test POSIX se omite en Windows; en CI Linux se ejecuta.
- El Node local es 26 y el CI usa 20; Vitest 4.1.12 soporta ambos.
- No se revisan CVEs de Python (010) ni se hace pentesting (009).
