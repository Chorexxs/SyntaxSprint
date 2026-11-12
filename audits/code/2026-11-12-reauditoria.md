# Auditoría de código — 2026-11-12 (cierre de la Fase 6)

| Campo | Valor |
| --- | --- |
| Tipo | Código y arquitectura (spec 008) |
| Fecha | 2026-11-12 |
| Auditor | Agente (OpenCode) |
| Alcance | Repo completo; foco en 2FA, rate limiting, analítica y tests JS |
| Commit auditado | `805d534` (`main`) |
| Herramientas | `code_metrics.py`, `pylint` 4.1.3, `isort`, `coverage` 7.17.2, `manage.py check/test`, `npm audit`, Vitest 4.1.12 |
| Resultado global | **8.9/10 (B)** · 0 CRÍTICOS, 0 ALTOS, 1 MEDIO, 1 BAJA y 1 INFO |

## 1. Alcance y exclusiones

- Incluido: `syntax_sprint/backend/` (incluye `totp.py`, `two_factor.py`,
  `middleware.py`, `ratelimit.py`, `analytics.py` y comandos), `syntax_sprint/`,
  plantillas, `static/js`, `tests/js`, migraciones y documentación de `specs/`.
- Excluido: `venv/`, `node_modules/`, CVEs de producción (ver 009), historial de git y
  pentesting. No se mide duplicación con `jscpd` ni Core Web Vitals (backlog).

## 2. Resumen ejecutivo

La Fase 6 de la spec 008 está cerrada: los dos hallazgos MEDIA de la auditoría
post-2FA (rate limit de `/admin/2fa/` y revocación de sesiones) están corregidos y
probados, y las 8 BAJAS restantes quedaron resueltas o mitigadas. La suite crece a
**88 tests Django + 14 JS** con **97 %** de cobertura, `pylint` se mantiene en
**10.00/10** y `npm audit` pasa de 6 avisos a **0**.

No hay errores funcionales conocidos ni deuda estructural nueva. Queda un MEDIA de
tooling: `code_metrics.py --strict` no reconoce como tests a los módulos `tests_*.py`,
así que el quality gate del CI falla con 14 falsos positivos (AUD-028), agravado por un
comando de 43 líneas (AUD-027). Un INFO documental: el backlog de 009 sigue listando la
CSP y la 2FA del admin como pendientes aunque ya están implementadas.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-027 | BAJA | Mantenibilidad | `backend/management/commands/enroll_admin_totp.py:45` | `code_metrics.py --strict` → `handle -> 43 líneas` | El quality gate falla y el comando concentra validación, persistencia y salida | Extraer `_save_device()` y `_report_result()`; dejar `handle` como orquestador | S | Cerrado (T008-32) |
| AUD-028 | MEDIA | Tooling / tests | `specs/tools/code_metrics.py:247` | `code_metrics.py --strict` lista 14 «funciones sin anotaciones» en `tests_ratelimit.py` y `tests_totp.py` | El quality gate del CI (`ci.yml:87`) está en rojo con código correcto; se normaliza ignorarlo | Excluir `tests*.py` (no solo `tests.py`) en `strict_violations` y `render` | S | Cerrado (T008-33) |
| AUD-029 | INFO | Documentación | `specs/009-cybersecurity/tasks.md:232-233` | «2FA para el admin» y «Cabecera CSP» siguen en `[ ]`; `T009-28`, `T009-30` y la spec 012 ya los implementan | Backlog engañoso sobre el estado real de seguridad | Eliminar o marcar ambos ítems como cubiertos | S | Cerrado (T009-36) |

> Sin secretos ni datos personales en este informe.

### Falsos positivos declarados (RNF-008-04)

| Señal | Motivo |
| --- | --- |
| 5 líneas > 100 en `backend/migrations/0001…0003` | Migraciones autogeneradas; se excluyen por decisión `T008-09`. |
| 14 funciones «sin anotaciones» en `tests_*.py` | El medidor solo excluye `tests.py`; los tests no requieren anotaciones. Es AUD-028. |

## 4. Métricas

| Métrica | Valor | Umbral | Estado |
| --- | --- | --- | --- |
| Archivos analizados | 38 | — | — |
| Líneas de código (Python/JS) | 2873 | — | — |
| Funciones | 159 | — | — |
| Funciones > 40 líneas | 1 (`enroll_admin_totp.py:45`, 43) | 0 | ⚠️ AUD-027 |
| Complejidad > 10 / anidamiento > 4 | 0 | 0 | ✅ |
| Funciones sin anotaciones | 0 reales (14 falsos positivos) | 0 | ⚠️ AUD-028 |
| Quality gate `--strict` | 15 incumplimientos (1 real + 14 falsos) | 0 | ❌ AUD-027/028 |
| `except` desnudo / `except Exception` | 0 | 0 | ✅ |
| `print()` en producción | 0 | 0 | ✅ |
| Riesgos JS (`eval`, `innerHTML`, `var`, `==`) | 0 | 0 | ✅ |
| Tests Django | 88 | — | ✅ |
| Tests JS | 14 | — | ✅ |
| Cobertura backend | 97 % (1196 sentencias, 32 sin cubrir) | ≥ 80 % | ✅ |
| Consultas en `/profile` | ≤ 5 (test con `CaptureQueriesContext`) | ≤ 5 | ✅ |
| Pylint | 10.00/10 | ≥ 8.0 | ✅ |
| isort | Sin avisos | 0 | ✅ |
| `manage.py check` | 0 issues | 0 | ✅ |
| `npm audit` (dev y producción) | 0 avisos | 0 | ✅ |
| Duplicación medida | No medida (`jscpd` pendiente) | < 3 % | ⚠️ backlog |
| p95 de `/get_python_function` | No medida | < 300 ms | ⚠️ backlog |

### Puntuación por dimensión

| Dimensión | Peso | Nota | Justificación |
| --- | ---: | ---: | --- |
| D1 Arquitectura | 20 % | 9 | Vistas por dominio, `totp`/`two_factor`/`ratelimit`/`analytics` separados; `views.py` en 11 líneas |
| D2 Escalabilidad | 20 % | 9 | Alias de caché configurables, paginación e índices; el límite de fragmentos es por worker (documentado) |
| D3 Legibilidad | 15 % | 8,5 | Nombres y tipos claros; `handle` de 43 líneas y `tests.py` de 971 líneas restan |
| D4 Errores | 15 % | 9 | `fail-open` con log, fallback de alias, contador atómico, 400/405/429 y validación JSON |
| D5 Testabilidad | 10 % | 9 | 102 tests, 97 % de cobertura, DOM/eventos y helpers puros; falta cobertura de ramas |
| D6 Rendimiento | 10 % | 9 | Una escritura menos por fragmento, ventana única por informe, perfil ≤ 5 consultas |
| D7 Frontend | 5 % | 9 | Sin `innerHTML`/`eval`/`var`; tests de DOM, pegado, reinicio y temporizadores limpiados |
| D8 Dependencias y docs | 5 % | 8 | Versiones fijadas y 0 CVEs; `code_metrics` deja el CI en rojo y el backlog de 009 está desalineado |

**Cálculo:** 0,20·9 + 0,20·9 + 0,15·8,5 + 0,15·9 + 0,10·9 + 0,10·9 + 0,05·9 +
0,05·8 = **8.9 → B**.

## 5. Comparación con la auditoría anterior

| Métrica | Post-2FA (2026-11-11) | Actual | Tendencia |
| --- | --- | --- | --- |
| Nota global | 8.25 (B) | 8.9 (B) | ▲ +0.65 |
| Archivos | 35 | 38 | ▲ |
| Funciones | 142 | 159 | ▲ |
| Tests | 74 + 8 | 88 + 14 | ▲ |
| Cobertura | 98 % | 97 % | ▼ leve (más código y tests nuevos) |
| Vulnerabilidades dev (npm) | 6 | 0 | ✅ |
| Hallazgos ALTA / MEDIA / BAJA | 0 / 2 / 8 | 0 / 1 / 1 | ✅ |

## 6. Acciones inmediatas (≤ 24 h)

1. Corregir AUD-027 y AUD-028 antes del próximo push a `main`: los dos incumplimientos
   dejan en rojo el job `Métricas de código` del CI (`code_metrics.py --strict`).
2. AUD-028 es MEDIA (SLA 30 días); AUD-027 y AUD-029 pueden ir en el mismo cambio.

## 7. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| AUD-027 | `T008-32` | `specs/008-code-audit` |
| AUD-028 | `T008-33` | `specs/008-code-audit` |
| AUD-029 | `T009-30` | `specs/009-cybersecurity` |

## 8. Comandos ejecutados

```bash
git status --short && git rev-parse --short HEAD
# 805d534; árbol limpio
python specs/tools/code_metrics.py --strict
# 38 archivos, 2873 líneas, 159 funciones; 1 función > 40 y 14 falsos positivos
cd syntax_sprint && python manage.py check
# System check identified no issues (0 silenced).
cd syntax_sprint && python manage.py test
# Ran 88 tests; OK (1 omitido en Windows por permisos POSIX)
cd syntax_sprint && coverage run --source=backend manage.py test && coverage report
# TOTAL 1196 sentencias, 32 sin cubrir, 97 %
isort --check-only syntax_sprint/
# Sin avisos
pylint syntax_sprint/backend syntax_sprint/syntax_sprint --score=y
# 10.00/10
npm audit && npm audit --omit=dev
# found 0 vulnerabilities
npm run test:js
# 14 tests OK (Vitest 4.1.12, jsdom)
```

Versiones: Python 3.12.1, pylint 4.1.3, coverage 7.17.2, Node 26.13.0, npm 12.2.2,
Vitest 4.1.12.

## 9. Limitaciones

- No se mide duplicación con `jscpd` ni rendimiento p95: siguen en el backlog de 008.
- La cobertura es de líneas, no de ramas; `ratelimit.py` queda en 76 % por las ramas
  de degradación.
- Un test POSIX se omite en Windows (permisos `0600`); en CI Linux se ejecuta.
- El Node local es 26 y el CI usa 20; Vitest 4.1.12 soporta ambos.
- La auditoría no revisa CVEs de Python (spec 010) ni hace pentesting (spec 009).
