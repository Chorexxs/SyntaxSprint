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

- [ ] **T005-05** Envolver `json.loads` en `try/except` y validar tipos numéricos.
  - Requisito: `RF-005-03`
  - Archivos: `backend/views.py`
  - DoD: cuerpo inválido o claves ausentes devuelven 400 sin traza.

- [ ] **T005-06** Validar rangos: `0 ≤ wpm ≤ 400`, `0 ≤ accuracy ≤ 100`, valores finitos.
  - Requisito: `RF-005-09`
  - Archivos: `backend/views.py`
  - DoD: `-1`, `101`, `NaN` e `Infinity` devuelven 400.

- [ ] **T005-07** Sustituir las dos agregaciones por una sola con `Avg` doble.
  - Requisito: `RF-005-06`
  - Archivos: `backend/views.py`
  - DoD: una sola consulta SQL en el perfil.

- [ ] **T005-08** Paginar el historial (20 por página) y eliminar `on_profile_page` si no se usa.
  - Requisito: `RF-005-10`
  - Archivos: `backend/views.py`, `templates/profile.html`
  - DoD: con 45 resultados hay 3 páginas navegables.

- [ ] **T005-09** Añadir `login_url="login"` al guardado y al perfil.
  - Requisito: `RF-005-08`
  - Archivos: `backend/views.py`
  - DoD: visitante termina en `/login`.

- [ ] **T005-10** Hacer la tabla responsive (scroll horizontal accesible o tarjetas en móvil).
  - Requisito: `RNF-005-04`
  - Archivos: `templates/profile.html`, `static/css/styles.css`

## Fase 3 — Verificación

- [ ] **T005-11** Tests de guardado válido, 400, 405, anónimo y aislamiento entre usuarios.
  - Requisitos: `CA-005-01`…`CA-005-07`
  - Archivos: `backend/tests.py`

- [ ] **T005-12** Test de promedios y de borrado en cascada.
  - Requisitos: `CA-005-05`, `RF-005-12`
  - Archivos: `backend/tests.py`

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
