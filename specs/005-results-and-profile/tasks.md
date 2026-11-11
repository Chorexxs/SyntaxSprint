# Tareas 005 — Resultados, perfil e historial

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/005-results-and-profile/spec.md`

## Fase 1 — Implementado

- [x] **T005-01** Crear el modelo `TypingTestResult` con FK a `User`, WPM, precisión y fecha.
  - Requisitos: `RF-005-01`, `RF-005-12`
  - Archivos: `backend/models.py`, `migrations/0001_initial.py`
  - DoD: migración aplicada y `__str__` legible.

- [x] **T005-02** Implementar `save_typing_test_result` con `login_required`, 400 y 405.
  - Requisitos: `RF-005-02`, `RF-005-03`, `RF-005-04`
  - Archivos: `backend/views.py`

- [x] **T005-03** Implementar el perfil con historial descendente y promedios.
  - Requisitos: `RF-005-05`, `RF-005-06`
  - Archivos: `backend/views.py`, `templates/profile.html`

- [x] **T005-04** Implementar el estado vacío del perfil con enlace a hacer un test.
  - Requisito: `RF-005-07`
  - Archivos: `templates/profile.html`

## Fase 2 — Robustez

- [x] **T005-05** Envolver `json.loads` en `try/except` y validar tipos numéricos.
  - Requisito: `RF-005-03`
  - Archivos: `backend/views.py`
  - DoD: cuerpo inválido o claves ausentes devuelven 400 sin traza.
  - Evidencia: tests `test_save_invalid_json` y `test_save_missing_fields`.

- [x] **T005-06** Validar rangos: `0 ≤ wpm ≤ 400`, `0 ≤ accuracy ≤ 100`, valores finitos.
  - Requisito: `RF-005-09`
  - Archivos: `backend/views.py`
  - DoD: `-1`, `101`, `NaN` e `Infinity` devuelven 400.
  - Evidencia: `math.isfinite` + rangos en `views.py:300-303`; test
    `test_save_out_of_range`.

- [x] **T005-07** Sustituir las dos agregaciones por una sola con `Avg` doble.
  - Requisito: `RF-005-06`
  - Archivos: `backend/views.py`
  - DoD: una sola consulta SQL en el perfil.
  - Evidencia: `results.aggregate(avg_wpm=Avg("wpm"), avg_accuracy=Avg("accuracy"))`.

- [x] **T005-08** Paginar el historial (20 por página) y eliminar `on_profile_page` si no se usa.
  - Requisito: `RF-005-10`
  - Archivos: `backend/result_views.py`, `templates/profile.html`, `backend/tests.py`
  - DoD: con 45 resultados hay 3 páginas navegables.
  - Evidencia: `Paginator(results, 20).get_page(...)`; `results` y `page_obj` comparten la
    página y `profile.html` muestra "anterior / página N de M / siguiente". Tests
    `test_profile_paginates_history` (45 filas → 20/20/5) y
    `test_profile_out_of_range_page_returns_last_page`. `on_profile_page` no existía en
    el código.

- [x] **T005-09** Añadir `login_url="login"` al guardado y al perfil.
  - Requisito: `RF-005-08`
  - Archivos: `backend/views.py`
  - DoD: visitante termina en `/login`.
  - Evidencia: tests `test_profile_requires_login` y `test_save_requires_login`.

- [x] **T005-10** Hacer la tabla responsive (scroll horizontal accesible o tarjetas en móvil).
  - Requisito: `RNF-005-04`
  - Archivos: `templates/profile.html`, `static/css/styles.css`
  - Evidencia: `profile.html:87` envuelve la tabla en `overflow-x-auto`.

## Fase 3 — Verificación

- [x] **T005-11** Tests de guardado válido, 400, 405, anónimo y aislamiento entre usuarios.
  - Requisitos: `CA-005-01`…`CA-005-07`
  - Archivos: `backend/tests.py`
  - Evidencia: `ResultTests` (6 casos) + `AuthTests.test_save_requires_login`.

- [ ] **T005-12** Test de promedios y de borrado en cascada.
  - Requisitos: `CA-005-05`, `RF-005-12`
  - Archivos: `backend/tests.py`
  - Estado: pendiente. No hay test que compruebe `avg_wpm`/`avg_accuracy` ni el
    borrado en cascada al eliminar un usuario.

## Deuda técnica / Backlog

- [ ] Añadir `language` y `duration_seconds` al modelo (nueva migración).
- [ ] Recalcular WPM en servidor a partir de `duration_seconds` y longitud del fragmento.
- [ ] Idempotencia del guardado con `client_token`.
- [ ] Ranking global y rachas.
- [ ] Exportar historial a CSV.
- [ ] Gráfica de evolución de WPM.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Auditoría del modelo, endpoint y perfil |
| 2026-11-11 | T005-08 cerrada: historial paginado a 20 por página |
