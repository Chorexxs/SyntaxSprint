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

- [x] **T004-14** Ejecutar el checklist manual del `plan.md` y registrar evidencia.
  - Requisitos: `CA-004-01`…`CA-004-09`
  - Evidencia (2026-11-11, Chrome DevTools, `runserver` local con BD SQLite temporal
    para no tocar datos de producción):
    - Ventana aislada sin sesión; "start" → `POST /get_python_function` 200, sin 403;
      el fragmento se muestra y el temporizador arranca en 30 (`CA-004-01`).
    - 5 caracteres correctos → 5 `letter.correct` en verde `rgb(46,125,50)`; 1
      incorrecto → `letter.incorrect` en rojo `rgb(192,57,43)` y precisión 83 %
      (`CA-004-04`).
    - Pegado de 200 caracteres → el input se trunca a 80 (longitud del fragmento) y
      el test termina (`CA-004-05`).
    - Temporizador a 0 → resultados visibles y POST de guardado (`CA-004-06`).
      Anónimo: 302 a login y mensaje "Inicia sesión para guardar tu resultado.";
      autenticado: 200 y "Resultado guardado.".
    - "try again" → fragmento distinto (`def greet…` → `d = {…}`), input vacío y
      contadores a 0 / 100 % (`CA-004-07`).
    - Usuario autenticado con WPM 4 y 100 % → `/profile` muestra promedio 4 y la fila
      del historial 4 / 100 % (`CA-004-08`).
    - `blur` de ventana → temporizador congelado en 28 durante 3 s (`CA-004-09`).
    - Enter, Escape, Tab y flecha izquierda → `defaultPrevented`; valor y foco intactos
      (`RF-004-09`).
    - Funciones puras: `computeWpm(5, 1) = 1`, `computeAccuracy(8, 2) = 80`, input
      vacío = 100 % (`CA-004-02`, `CA-004-03`).
    - Sin errores en consola ni peticiones fallidas durante el recorrido.

- [x] **T004-15** Decidir el destino de las métricas avanzadas (`spacing`, `duration`, `afkHistory`, `errorHistory`).
  - Requisito: `RF-004-15` (retirado)
  - Decisión: eliminarlas. No se mostraban en ninguna vista y añadían estado y handlers
    globales sin uso.
  - Evidencia: retirados los campos del estado, los resets, `handleGlobalKeydown`/`Keyup`,
    `keysToTrack` y el bloque de duraciones de `endTest`; `node --check` OK y sin
    referencias restantes. `RF-004-15` eliminado de la spec y la trazabilidad.

- [x] **T004-16** Añadir pruebas automatizadas de las fórmulas y del conteo del motor.
  - Requisitos: `RNF-004-06`
  - Archivos: `tests/js/script.test.js`, `vitest.config.mjs`, `package.json`
  - Evidencia: 8 tests con Vitest + jsdom (`computeWpm`, `computeAccuracy` y
    `TypingTest.countTypedChars`); `npm run test:js` en verde y en CI.

## Fase 4 — Código multilínea y pausa (2026-11-12)

- [x] **T004-17** Permitir escribir saltos de línea con Enter.
  - Requisitos: `RF-004-09`, `CA-004-10`
  - Archivos: `static/js/script.js`, `tests/js/script.test.js`
  - Evidencia: Enter ya no se bloquea en `handleKeydown`; el textarea inserta `\n` y
    `handleInput` lo cuenta. En Chrome: `class MyContext:` + Enter → 17 correctos, 0
    incorrectos y el `\n` en verde. Test: `no bloquea Enter y cuenta el salto de línea`.
  - DoD: un fragmento multilínea se puede completar con Enter. ✅

- [x] **T004-18** Insertar la indentación esperada con Tab.
  - Requisito: `RF-004-09`
  - Archivos: `static/js/script.js`, `tests/js/script.test.js`
  - Evidencia: `insertIndentation()` añade el tramo de espacios (2/4/8) que espera el
    fragmento; se elimina el listener muerto de `promptDisplay`. En Chrome insertó los 4
    espacios de la línea siguiente (21 correctos, 0 incorrectos). Tests de Tab con 2, 4
    y 8 espacios y a mitad de línea sin indentación.
  - DoD: `CA-004-11` y test de Tab en línea indentada y a mitad de línea. ✅

- [x] **T004-19** Excluir el tiempo en pausa del WPM.
  - Requisitos: `RF-004-14`, `RNF-004-07`, `CA-004-12`
  - Archivos: `static/js/script.js`, `tests/js/script.test.js`
  - Evidencia: `pausedMs`/`pauseStartedAt` y `elapsedMinutes()`; `updateLiveStats` y
    `endTest` usan el tiempo efectivo. En Chrome, pausa de 2,6 s: timer 29→28 y WPM
    395→183 (solo tiempo activo), frente a 83 con el cálculo anterior. Test con
    temporizadores falsos.
  - DoD: tras pausar 2 s, el WPM no baja. ✅

- [x] **T004-20** Evitar la duplicación de caracteres IME.
  - Requisito: `RF-004-13`
  - Archivos: `static/js/script.js`, `tests/js/script.test.js`
  - Evidencia: `handleCompositionEnd` recalcula desde `input.value` sin concatenar
    `e.data`; en Chrome una composición de `á` deja `"á"`. Test de composición.
  - DoD: una composición deja un solo carácter y los contadores cuadran. ✅

- [x] **T004-21** Reiniciar el timer visual al comenzar.
  - Requisitos: `RF-004-02`, `RNF-004-02`
  - Archivos: `static/js/script.js`, `tests/js/script.test.js`
  - Evidencia: `startTest` escribe `timeLeft` en `#timer`; en Chrome, al iniciar y tras
    "try again" se ve 30, no el 0 anterior. Test de `startTest` con `fetch` simulado.
  - DoD: el timer nunca muestra el valor del test anterior. ✅

- [x] **T004-22** Auto-indentar al pulsar Enter.
  - Requisitos: `RF-004-09`, `CA-004-10`
  - Archivos: `static/js/script.js`, `tests/js/script.test.js`
  - Evidencia: `insertNewline()` añade `\n` más el tramo de espacios (2/4/8) de la línea
    siguiente; fuera de un salto esperado inserta solo `\n`. En Chrome, `def add(a, b):`
    + Enter dejó `"def add(a, b):\n    "` con 19/19 correctos y el cursor en `return`;
    el fragmento terminó con 100 %. Tests de auto-indentación y de salto fuera de
    contexto.
  - DoD: tras Enter el cursor queda en el primer carácter del código y no hay que pulsar
    espacio ni Tab para la indentación. ✅

## Deuda técnica / Backlog

- [x] Tests automatizados de frontend (Vitest + jsdom); DOM y eventos cubiertos en `T008-31`.
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
| 2026-11-11 | T004-16: pruebas de frontend con Vitest + jsdom |
| 2026-11-12 | Revisión en navegador: Enter/Tab, pausa, IME y timer (T004-17…T004-21) |
| 2026-11-12 | T004-17…T004-21 cerradas: código multilínea, pausa e IME corregidos |
| 2026-11-12 | T004-22: Enter auto-indenta con los espacios de la línea siguiente |
