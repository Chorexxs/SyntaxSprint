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

- [x] **T006-10** Añadir labels accesibles a los inputs de login y signup.
  - Requisito: `RF-006-07`
  - Archivos: `templates/login.html`, `templates/signup.html`
  - Evidencia: los 6 inputs tienen `<label for="...">` con clase `sr-only` e `id` único
    (`login-username`, `login-password`, `signup-username`, `signup-email`,
    `signup-password`, `signup-password2`). Verificado en Chrome: `input.labels`
    devuelve "Usuario", "Contraseña", "Correo electrónico" y "Confirmar contraseña".

- [x] **T006-11** Añadir `role="alert"` a los mensajes y `scope="col"` a la tabla.
  - Requisito: `RF-006-07`
  - Archivos: `templates/login.html`, `templates/signup.html`, `templates/profile.html`
  - Evidencia: `role="alert"` presente en los bloques de mensajes de login y signup;
    los tres `<th>` de `profile.html:35-37` llevan `scope="col"`.

- [x] **T006-12** Revisar contraste de `--text-sub` en ambos temas y ajustar si < 4.5:1.
  - Requisito: `RNF-000-05`
  - Archivos: `static/css/styles.css`, `templates/base.html`, `templates/index.html`
  - DoD: ratios WCAG AA ≥ 4.5:1 y Lighthouse Accessibility ≥ 95.
  - Evidencia: `--text-sub` pasa de 2.17–2.40:1 a 4.54–5.69:1; `--error` a 4.98/4.99:1
    y `--success` claro a 4.70:1. Footer sin opacidad `/60`, `::placeholder` con el token
    y `<label>` para `#language-select`. Detalle y limitaciones en `plan.md` §10.
  - Nota: con Tailwind compilado, Lighthouse (desktop) da **Accessibility 100**,
    Best Practices 100 y SEO 100; `axe-core` no reporta violaciones.

## Fase 4 — Verificación

- [x] **T006-13** Checklist responsive en 320, 768 y 1440 px.
  - Requisitos: `RF-006-05`, `CA-006-03`
  - Evidencia: las 4 páginas en 320/768/1440 px con Chrome: `innerWidth = clientWidth =
    scrollWidth` y ningún elemento fuera del viewport. A 320 px el selector y el botón
    caben, logo y nav no se solapan y el prompt usa 14 px.

- [x] **T006-14** Checklist de tema entre las 4 páginas y recarga.
  - Requisitos: `CA-006-01`, `CA-006-02`
  - Evidencia: con tema claro guardado, las 4 páginas y la recarga mantienen
    `data-theme="light"` y fondo `#f5f5f5`; con oscuro, `#323437`. La preferencia
    guardada prevalece sobre la del sistema.

- [x] **T006-15** Respetar `prefers-color-scheme` cuando no hay preferencia.
  - Requisito: `RF-006-09`
  - Archivos: `static/js/theme-init.js`
  - Evidencia: con `localStorage` vacío, emular `prefers-color-scheme: light` aplica el
    tema claro y `dark` aplica el oscuro; con una preferencia guardada, esta gana.

## Deuda técnica / Backlog

- [x] Compilar Tailwind localmente y eliminar el CDN (ver 007).
  - Evidencia: `package.json`, `tailwind.config.js` y `npm run build:css` generan
    `static/css/tailwind.css`; `base.html` ya no carga el CDN ni scripts/config inline.
  - Fecha: 2026-11-11.
- [ ] Modo de alto contraste.
- [ ] Iconos SVG reutilizables como partial.
- [ ] Revisar tipografía en pantallas grandes (> 1920 px).

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Auditoría de plantillas y tokens |
| 2026-11-11 | T006-08 cerrada: foco visible con `:focus-visible` |
| 2026-11-11 | T006-10 y T006-11 cerradas: labels accesibles y `scope="col"` |
| 2026-11-11 | T006-12 cerrada: tokens ajustados a contraste WCAG AA |
| 2026-11-11 | Tailwind compilado localmente; CDN y scripts inline eliminados |
| 2026-11-11 | T006-13/14/15 cerradas: responsive, tema y `prefers-color-scheme` |
