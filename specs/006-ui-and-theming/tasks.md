# Tareas 006 — Sistema visual, temas y responsividad

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/006-ui-and-theming/spec.md`

## Fase 1 — Implementado

- [x] **T006-01** Definir tokens CSS para tema oscuro y claro.
  - Requisitos: `RF-006-01`, `RF-006-03`
  - Archivos: `static/css/styles.css`
  - DoD: `data-theme="light"` cambia todos los tokens.

- [x] **T006-02** Implementar toggle de tema con persistencia en `localStorage`.
  - Requisito: `RF-006-02`
  - Archivos: `templates/*.html`, `script.js`

- [x] **T006-03** Estilizar estados del prompt (correcto, incorrecto, activo, caret).
  - Requisito: `RF-006-06`
  - Archivos: `static/css/styles.css`

- [x] **T006-04** Aplicar tipografía monoespaciada y layout responsive básico.
  - Requisitos: `RF-006-05`, `RNF-006-04`
  - Archivos: `styles.css`, `templates/*.html`

## Fase 2 — Deduplicación

- [x] **T006-05** Crear `templates/base.html` con head, header, footer y bloques.
  - Requisito: `RF-006-04`
  - Archivos: `templates/base.html`
  - DoD: las 4 páginas lo extienden y no duplican el header.
  - Evidencia: las 4 plantillas usan `{% extends "base.html" %}`; cada página
    renderiza un único `<header>` y un único CDN de Tailwind (verificado con
    `django.test.Client`).

- [x] **T006-06** Extraer `static/js/theme.js` y eliminar los 4 scripts inline duplicados.
  - Requisitos: `RF-006-02`, `RF-006-03`
  - Archivos: `static/js/theme.js`, `templates/*.html`
  - DoD: un solo punto de inicialización de tema.
  - Evidencia: `theme.js` concentra toggle, iconos, `aria` y persistencia; `script.js`
    ya no contiene lógica de tema y las 4 plantillas no tienen scripts duplicados.

- [x] **T006-07** Aplicar el tema antes del primer pintado para evitar FOUC.
  - Requisito: `RNF-006-01`
  - Archivos: `base.html`
  - DoD: sin destello claro al recargar en tema oscuro.
  - Evidencia: script inline único en `<head>` que fija `data-theme` antes de cargar
    CSS y Tailwind; protege `localStorage` con `try/catch`.

## Fase 3 — Accesibilidad

- [x] **T006-08** Sustituir `*:focus { outline: none }` por `:focus-visible` con contorno visible.
  - Requisitos: `RF-006-07`, `RNF-006-03`
  - Archivos: `static/css/styles.css`, `templates/index.html`, `templates/login.html`,
    `templates/signup.html`
  - DoD: Tab muestra foco en logo, toggle, inputs y botones.
  - Evidencia: `styles.css:45-54` define `:focus-visible` con `outline: 2px solid
    var(--caret)` y retira el contorno solo en `:focus:not(:focus-visible)`. Se eliminó
    `focus:outline-none` de los 7 controles que lo usaban. Verificado en Chrome: Tab
    muestra un contorno sólido de 2 px en logo, toggle, enlaces, `#language-select`,
    botones y los 6 inputs de login/signup.

- [x] **T006-09** Añadir `aria-label` al toggle y `aria-pressed` dinámico.
  - Requisito: `RF-006-08`
  - Archivos: `base.html`, `theme.js`
  - Evidencia: `aria-label` inicial en `base.html` y `theme.js` actualiza
    `aria-label` y `aria-pressed` según el tema activo.

- [ ] **T006-10** Añadir labels accesibles a los inputs de login y signup.
  - Requisito: `RF-006-07`
  - Archivos: `templates/login.html`, `templates/signup.html`
  - Estado: pendiente. Los 6 `<input>` no tienen `<label>` asociado ni `aria-label`.

- [ ] **T006-11** Añadir `role="alert"` a los mensajes y `scope="col"` a la tabla.
  - Requisito: `RF-006-07`
  - Archivos: `templates/*.html`
  - Estado: parcial. `role="alert"` ya está en login y signup; falta `scope="col"` en
    los `<th>` de `profile.html:91-93`.

- [ ] **T006-12** Revisar contraste de `--text-sub` en ambos temas y ajustar si < 4.5:1.
  - Requisito: `RNF-000-05`
  - Archivos: `static/css/styles.css`
  - DoD: Lighthouse Accessibility ≥ 95.

## Fase 4 — Verificación

- [ ] **T006-13** Checklist responsive en 320, 768 y 1440 px.
  - Requisitos: `RF-006-05`, `CA-006-03`

- [ ] **T006-14** Checklist de tema entre las 4 páginas y recarga.
  - Requisitos: `CA-006-01`, `CA-006-02`

- [ ] **T006-15** Respetar `prefers-color-scheme` cuando no hay preferencia.
  - Requisito: `RF-006-09`
  - Archivos: `theme.js`

## Deuda técnica / Backlog

- [ ] Compilar Tailwind localmente y eliminar el CDN (ver 007).
- [ ] Modo de alto contraste.
- [ ] Iconos SVG reutilizables como partial.
- [ ] Revisar tipografía en pantallas grandes (> 1920 px).

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Auditoría de plantillas y tokens |
| 2026-11-11 | T006-08 cerrada: foco visible con `:focus-visible` |
