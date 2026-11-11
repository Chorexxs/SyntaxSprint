# Tareas 004 — Motor de test de mecanografía

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/004-typing-engine/spec.md`

## Fase 1 — Implementado

- [x] **T004-01** Implementar inicio de test: fetch del fragmento, reset de estado y foco en el input.
  - Requisitos: `RF-004-01`
  - Archivos: `static/js/script.js`

- [x] **T004-02** Implementar render por carácter con estados `correct`, `incorrect` y `active`.
  - Requisito: `RF-004-03`
  - Archivos: `script.js`, `static/css/styles.css`

- [x] **T004-03** Implementar temporizador de 30 s con fin automático.
  - Requisitos: `RF-004-02`, `RF-004-10`

- [x] **T004-04** Implementar cálculo de WPM y precisión al finalizar y en vivo.
  - Requisitos: `RF-004-04`, `RF-004-05`, `RF-004-06`

- [x] **T004-05** Implementar pegado truncado, backspace y bloqueo de atajos.
  - Requisitos: `RF-004-07`, `RF-004-08`, `RF-004-09`

- [x] **T004-06** Implementar resultados, "try again" y envío del resultado al backend.
  - Requisitos: `RF-004-11`, `RF-004-12`

- [x] **T004-07** Implementar soporte IME y pausa al perder foco.
  - Requisitos: `RF-004-13`, `RF-004-14`

## Fase 2 — Correcciones

- [x] **T004-08** Añadir `{% csrf_token %}` a `index.html` para inicializar la cookie CSRF.
  - Requisito: `RNF-004-05`
  - Archivos: `templates/index.html`
  - DoD: en ventana privada, el POST de inicio responde 200 y no 403.
  - Evidencia: `index.html:44` y `index.html:66`; test `test_index_sets_csrf_cookie`.

- [x] **T004-09** Manejar la respuesta de `saveResult`: distinguir 200, 302 (anónimo), 403 y 500, y mostrar aviso.
  - Requisito: `RF-004-12`
  - Archivos: `script.js`, `templates/index.html`
  - DoD: usuario anónimo ve "inicia sesión para guardar tu resultado".
  - Evidencia: `saveResult` usa `redirect: 'manual'`, detecta `opaqueredirect`/302,
    trata `!response.ok` y muestra aviso en `#save-status`.

- [x] **T004-10** Corregir la desincronización de `totalChars` tras backspace y pegado.
  - Requisitos: `RF-004-07`, `RF-004-08`
  - Archivos: `script.js`
  - DoD: escribir 3, borrar 1 y escribir 2 deja `totalChars = 4`.
  - Evidencia: `countTypedChars(value)` recalcula los tres contadores desde el input y se
    usa en `handleInput`, `handleKeydown` (Backspace), `handlePaste` y
    `compositionend`. Verificado en Chrome: 3 → backspace → 2 → 2 más = 4 caracteres
    correctos con 100 % de precisión; pegar 1 correcto + 4 erróneos muestra 20 % y tras
    un backspace, 25 %.

- [x] **T004-11** Extraer `computeWpm()` y `computeAccuracy()` como funciones puras y reutilizarlas.
  - Requisitos: `RF-004-04`, `RF-004-05`
  - Archivos: `script.js`
  - DoD: mismo resultado en vivo y al final; sin duplicar fórmulas.
  - Evidencia: ambas funciones viven junto a `keysToTrack` y las usan
    `updateLiveStats` y `endTest`. Verificado en Chrome: `computeWpm(5, 1) = 1`
    (`CA-004-02`), `computeAccuracy(8, 2) = 80` (`CA-004-03`), vacío = 100 % y
    tiempo 0 = 0 WPM.

- [x] **T004-12** Eliminar el atributo `value=""` del `<textarea>` y añadir `aria-label`.
  - Requisito: `RNF-004-04`
  - Archivos: `templates/index.html`
  - Evidencia: `index.html:125` sin `value=""` y con `aria-label="Typing input"`.

- [x] **T004-13** Garantizar limpieza de `timerInterval` en fin, reinicio y `blur`.
  - Requisito: `RNF-004-02`
  - Archivos: `script.js`
  - DoD: tras 3 reinicios solo hay un intervalo activo.
  - Evidencia: `stopTimer()` centraliza `clearInterval` + `timerInterval = null` y se
    llama al inicio de `startTest`, de `startTimer`, en `endTest` y en `blur`. Medido en
    Chrome instrumentando `setInterval`: 1 intervalo activo tras iniciar y 1 tras
    reiniciar (antes quedaban 2).

## Fase 3 — Verificación

- [ ] **T004-14** Ejecutar el checklist manual del `plan.md` y registrar evidencia.
  - Requisitos: `CA-004-01`…`CA-004-09`

- [x] **T004-15** Decidir el destino de las métricas avanzadas (`spacing`, `duration`, `afkHistory`, `errorHistory`).
  - Requisito: `RF-004-15` (retirado)
  - Decisión: eliminarlas. No se mostraban en ninguna vista y añadían estado y handlers
    globales sin uso.
  - Evidencia: retirados los campos del estado, los resets, `handleGlobalKeydown`/`Keyup`,
    `keysToTrack` y el bloque de duraciones de `endTest`; `node --check` OK y sin
    referencias restantes. `RF-004-15` eliminado de la spec y la trazabilidad.

## Deuda técnica / Backlog

- [ ] Tests automatizados de frontend (Vitest + jsdom o Playwright).
- [ ] Modos de test configurables (15/30/60 s, palabras).
- [ ] Mostrar progreso del fragmento (carácter actual / total).
- [ ] Reintento automático del guardado con backoff.
- [ ] Modo "focus" sin header.

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Auditoría del motor existente y plan de correcciones |
| 2026-11-11 | T004-10 y T004-13 cerradas: contadores recalculados y temporizador único |
| 2026-11-11 | T004-11 cerrada: WPM y precisión como funciones puras |
| 2026-11-11 | T004-15 cerrada: métricas avanzadas eliminadas por no usarse |
