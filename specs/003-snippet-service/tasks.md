# Tareas 003 — Servicio de fragmentos de código

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/003-snippet-service/spec.md`

## Fase 1 — Implementado

- [x] **T003-01** Crear catálogo de 8 lenguajes con 15 fragmentos cada uno.
  - Requisitos: `RF-003-01`, `RF-003-06`
  - Archivos: `backend/views.py`
  - DoD: `code_snippets` contiene las 8 claves y todas las listas tienen 15 elementos.

- [x] **T003-02** Devolver un fragmento aleatorio con `random.choice`.
  - Requisito: `RF-003-02`
  - DoD: dos llamadas consecutivas pueden devolver fragmentos distintos.

- [x] **T003-03** Implementar fallback a Python para lenguajes desconocidos.
  - Requisito: `RF-003-03`
  - DoD: `{"language": "cobol"}` devuelve un fragmento Python.

- [x] **T003-04** Soportar GET (Python por defecto) y POST con `{"language"}`.
  - Requisito: `RF-003-05`
  - Archivos: `backend/views.py`, `backend/urls.py`

## Fase 2 — Refactor y robustez

- [x] **T003-05** Extraer el catálogo a `backend/snippets.py` con `CODE_SNIPPETS` y `pick_snippet()`.
  - Requisito: `RNF-003-02`
  - Archivos: `backend/snippets.py`, `backend/views.py`
  - DoD: `views.py` < 60 líneas y la vista importa el helper.
  - Evidencia: `snippets.py` con `CODE_SNIPPETS` (8 lenguajes × 15 fragmentos) y
    `pick_snippet()`; `get_python_function` en `snippet_views.py` (16 líneas) y
    `views.py` reducido a 7 líneas tras `T008-11`.
  - Nota: el DoD de "< 60 líneas" se cumple tras `T008-11`. El catálogo extraído es
    idéntico al original (verificado con `ast`); los 26 tests siguen en verde.

- [x] **T003-06** Envolver `json.loads` en `try/except` y responder 400 con `{"error": "Cuerpo JSON inválido"}`.
  - Requisito: `RF-003-07`
  - Evidencia: test `test_invalid_json_returns_400`.
  - DoD: `client.post(url, data="{", content_type="application/json")` devuelve 400.

- [x] **T003-07** Añadir `@require_http_methods(["GET", "POST"])`.
  - Requisito: `RF-003-05`
  - Evidencia: test `test_put_not_allowed`.
  - DoD: `PUT` devuelve 405.

- [ ] **T003-08** Validar en tiempo de importación que cada snippet tenga `name` y `code` no vacíos.
  - Requisito: `RNF-003-03`
  - Archivos: `backend/snippets.py`
  - DoD: un fragmento inválido falla al arrancar, no en producción.

## Fase 3 — Verificación

- [ ] **T003-09** Tests de contrato: válido, desconocido, GET, JSON inválido, catálogo completo.
  - Archivos: `backend/tests.py`
  - DoD: 5 casos del plan en verde.
  - Estado: 4 de 5 casos en `SnippetTests` (válido, desconocido, GET, JSON inválido).
    Falta el caso de catálogo completo (8 claves × 15 fragmentos).

- [ ] **T003-10** Test de aleatoriedad con al menos 3 nombres distintos en 20 llamadas.
  - Requisito: `RF-003-02`
  - DoD: no usa `random.seed` global; usa `unittest.mock.patch` si es necesario.

## Deuda técnica / Backlog

- [ ] Añadir alias `/api/snippets/random` manteniendo la ruta antigua.
- [ ] Añadir `Cache-Control: no-store` para evitar fragmentos cacheados.
- [ ] Nuevos lenguajes: Rust, C++, C#, Kotlin.
- [ ] Metadatos de dificultad y longitud estimada.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Auditoría del catálogo y contrato actuales |
