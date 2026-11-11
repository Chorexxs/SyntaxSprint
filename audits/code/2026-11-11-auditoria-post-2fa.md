# Auditoría de código — 2026-11-11 (post-2FA y tests JS)

| Campo | Valor |
| --- | --- |
| Tipo | Código y arquitectura (spec 008) |
| Fecha | 2026-11-11 |
| Auditor | Agente (OpenCode) |
| Alcance | Repo completo; foco en caché compartida, 2FA, tests JS y migraciones nuevas |
| Commit auditado | `db28f69` (`main`) |
| Herramientas | `code_metrics.py`, `pylint`, `isort`, `coverage`, `manage.py check`, `npm audit`, `npm run test:js` |
| Resultado global | **8.25/10 (B)** · sin hallazgos ALTA |

## 1. Alcance y exclusiones

- Incluido: `backend/` (incluye `totp.py`, `two_factor.py`, `ratelimit.py`), `syntax_sprint/`,
  plantillas, `static/js`, `tests/js`, migraciones y documentación de `specs/`.
- Excluido: `venv/`, `node_modules/`, CVEs de producción (ver 009/010), historial de git
  y pentesting.

## 2. Resumen ejecutivo

No hay errores funcionales en los caminos principales: TOTP verifica con comparación en
tiempo constante, ventana ±1 y protección de replay; el rate limiting degrada a
"permitir" si la caché falla; y el flujo de 2FA está cubierto por 14 tests. La suite pasa
completa (74 Django + 8 JS) y el quality gate está limpio.

El riesgo nuevo está en los bordes del 2FA: **no hay límite de intentos en
`/admin/2fa/`** (un atacante con la contraseña podría probar códigos) y **desactivar o
rotar el TOTP no invalida las sesiones ya verificadas**. Ambos son MEDIA y se corrigen
sin rediseño. El resto son mejoras de robustez, rendimiento y tests.

## 3. Hallazgos

| ID | Severidad | Categoría | Ubicación | Evidencia | Impacto | Recomendación | Esfuerzo | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AUD-017 | MEDIA | Seguridad / abuso | `backend/two_factor.py:17-39`, `backend/middleware.py:46-52` | `/admin/2fa/` está exento del middleware y no llama a `is_rate_limited`; no hay contador de fallos | Fuerza bruta del código de 6 dígitos si la contraseña del staff ya está comprometida | Reutilizar `is_rate_limited` con ámbito `admin-2fa` (5/300 s), bloquear tras N fallos y registrar el evento | S | Abierto |
| AUD-018 | MEDIA | Seguridad / sesión | `backend/middleware.py:71-77`, `enroll_admin_totp.py:32-43` | El middleware solo comprueba `session["admin_totp_ok"]`; `--disable` y la rotación no tocan las sesiones | Un dispositivo perdido sigue teniendo acceso hasta 2 semanas aunque se desactive el TOTP | Guardar una versión del dispositivo en la sesión y compararla, o borrar las sesiones del usuario al rotar/desactivar | M | Abierto |
| AUD-019 | BAJA | Secretos / operación | `enroll_admin_totp.py:44-46` | El comando imprime secreto y URI en stdout; la Shell de Render captura la salida | El secreto puede quedar en logs del proveedor | Añadir `--write <archivo>` (0600) o una pantalla de enrolamiento de un solo uso; documentar limpiar logs | S | Abierto |
| AUD-020 | BAJA | Rendimiento | `settings.py:122-131`, `ratelimit.py:22-24`, `snippet_views.py:19`, `analytics.py:25-31` | `RATE_LIMIT_CACHE_ALIAS=shared` se usa también para fragmentos: cada petición hace `cache.add/incr` en BD **y** un `INSERT` de analítica | Dos escrituras por petición en el endpoint más caliente | Usar caché compartida solo para auth y LocMem para fragmentos, o migrar a Redis | S/M | Abierto |
| AUD-021 | BAJA | Mantenibilidad | `ratelimit.py:41-65,85-96` | `is_rate_limited` e `increment_counter` duplican `add`/`incr`/`set`; solo capturan `DatabaseError` | Un alias inválido (`InvalidCacheBackendError`) produce 500 en login y fragmentos | Extraer un `_bump_counter` común, validar el alias al arrancar y capturar `ImproperlyConfigured` | S | Abierto |
| AUD-022 | BAJA | Concurrencia | `two_factor.py:30-33` | Lee `last_counter`, verifica y guarda sin bloqueo; dos POST simultáneos con el mismo código pueden aceptarse | Replay doble en una ventana muy estrecha | Actualización condicional (`filter(last_counter__lt=counter).update(...)`) o `select_for_update` | S | Abierto |
| AUD-023 | BAJA | Cabeceras | `two_factor.py:17-39` | La página de verificación no usa `@never_cache` y contiene token CSRF y estado de sesión | Caché intermedia podría servir una página ajena | Añadir `@never_cache` | S | Abierto |
| AUD-024 | BAJA | Tests | `tests.py:667-674`, `tests.py:788-792` | `test_default_alias_is_local` y `test_middleware_disabled_by_default` leen settings del entorno | Fallan si CI define `RATE_LIMIT_CACHE_ALIAS` o `ADMIN_TOTP_REQUIRED` | Usar `override_settings` explícito en ambos tests | S | Abierto |
| AUD-025 | BAJA | Dependencias dev | `package.json:10-13` | `npm audit`: 6 avisos (3 moderate, 1 high, 2 critical) en `tinypool`/`vitest 2.1.9`; `npm audit --omit=dev` → 0 | RCE solo en el runner de tests, no en producción | Actualizar Vitest (breaking) en una tarea de 010 y revalidar Node 20 | M | Abierto |
| AUD-026 | BAJA | Testabilidad frontend | `tests/js/script.test.js:16-65` | Solo cubre fórmulas y `countTypedChars`; no hay DOM, eventos, pegado ni `updateDisplay` | Regresiones de UI seguirían pasando el CI | Añadir tests con jsdom para `updateDisplay`, `handlePaste` y reinicio | M | Abierto |

> Sin secretos ni datos personales en este informe.

## 4. Métricas

| Métrica | Valor | Umbral | Estado |
| --- | --- | --- | --- |
| Archivos analizados | 35 | — | — |
| Líneas de código (Python/JS) | 2572 | — | — |
| Funciones | 142 | — | — |
| Funciones > 40 líneas / complejidad > 10 / anidamiento > 4 | 0 | 0 | ✅ |
| Funciones sin anotaciones | 0 | 0 | ✅ |
| `except` desnudo / `except Exception` | 0 | 0 | ✅ |
| Tests Django | 74 | — | ✅ |
| Tests JS | 8 | — | ✅ |
| Cobertura backend | 98 % (1014 sentencias, 25 sin cubrir) | ≥ 80 % | ✅ |
| Pylint | 10.00/10 | ≥ 8.0 | ✅ |
| isort | Sin avisos (root y `syntax_sprint/`) | 0 | ✅ |
| `check --deploy` (`DEBUG=False`) | 0 issues | 0 | ✅ |
| Vulnerabilidades producción (Python/JS) | 0 | 0 | ✅ |
| Vulnerabilidades dev (npm) | 6 (tinypool/vitest) | 0 | ⚠️ AUD-025 |

### Puntuación por dimensión

| Dimensión | Peso | Nota | Justificación |
| --- | ---: | ---: | --- |
| D1 Arquitectura | 20 % | 9 | Módulos separados (`totp`, `two_factor`, `ratelimit`), middleware y comandos cohesionados |
| D2 Escalabilidad | 20 % | 8 | Caché compartida entre workers; el alias único castiga el endpoint caliente |
| D3 Legibilidad | 15 % | 8,5 | Nombres y tipos claros; duplicación en el contador |
| D4 Errores | 15 % | 8 | `fail-open` correcto; faltan alias inválido y carrera del contador |
| D5 Testabilidad | 10 % | 8,5 | 82 tests y 98 %; frontend limitado a lógica pura |
| D6 Rendimiento | 10 % | 7,5 | Dos escrituras por petición de fragmentos |
| D7 Frontend | 5 % | 8 | Sin `innerHTML`/`eval`; tests JS parciales |
| D8 Dependencias y docs | 5 % | 7,5 | Producción limpia; dev con 6 avisos |

**Cálculo:** 0,20·9 + 0,20·8 + 0,15·8,5 + 0,15·8 + 0,10·8,5 + 0,10·7,5 + 0,05·8 +
0,05·7,5 = **8,25 → B**.

## 5. Comparación con la auditoría anterior

| Métrica | Post-analítica | Actual | Tendencia |
| --- | --- | --- | --- |
| Nota global | 8,55 (B) | 8,25 (B) | ▼ leve |
| Archivos | 30 | 35 | ▲ |
| Funciones | 94 | 142 | ▲ |
| Hallazgos ALTA | 0 | 0 | = |
| Tests | 52 | 74 + 8 | ▲ |
| Cobertura | 99 % | 98 % | ▼ leve |
| Vulnerabilidades dev | 0 | 6 | ▲ (AUD-025) |

## 6. Acciones inmediatas (≤ 24 h)

1. Ninguna bloqueante. AUD-017 y AUD-018 son MEDIA y la 2FA sigue **desactivada** en
   producción (`ADMIN_TOTP_REQUIRED=False`), lo que reduce la exposición actual.

## 7. Tareas y specs creadas

| Hallazgo | Tarea | Spec |
| --- | --- | --- |
| AUD-017 | T008-22 | `specs/008-code-audit` |
| AUD-018 | T008-23 | `specs/008-code-audit` |
| AUD-019 | T008-24 | `specs/008-code-audit` |
| AUD-020 | T008-25 | `specs/008-code-audit` |
| AUD-021 | T008-26 | `specs/008-code-audit` |
| AUD-022 | T008-27 | `specs/008-code-audit` |
| AUD-023 | T008-28 | `specs/008-code-audit` |
| AUD-024 | T008-29 | `specs/008-code-audit` |
| AUD-025 | T008-30 | `specs/008-code-audit`, `010-dependencies` |
| AUD-026 | T008-31 | `specs/008-code-audit` |

## 8. Comandos ejecutados

```bash
git status --short && git rev-parse --short HEAD
python specs/tools/code_metrics.py
cd syntax_sprint && python manage.py check
cd syntax_sprint && python manage.py makemigrations --check --dry-run
cd syntax_sprint && DEBUG=False python manage.py check --deploy
cd syntax_sprint && python manage.py test
cd syntax_sprint && python -m pylint backend --rcfile=../.pylintrc
python -m isort --check-only syntax_sprint/
cd syntax_sprint && python -m isort --check-only .
python -m coverage run --source=backend manage.py test
python -m coverage report --skip-covered
npm run test:js
npm audit
npm audit --omit=dev
```

## 9. Limitaciones

- No se reejecutó pentesting ni pruebas de carga.
- La cobertura de frontend no se mide con instrumentación; solo se cuentan los casos.
- Los avisos de `npm audit` afectan al entorno de tests, no al bundle desplegado.
- La auditoría es de solo lectura: los hallazgos no se corrigen aquí.
