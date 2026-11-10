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

- [ ] **T004-10** Corregir la desincronización de `totalChars` tras backspace y pegado.
  - Requisitos: `RF-004-07`, `RF-004-08`
  - Archivos: `script.js`
  - DoD: escribir 3, borrar 1 y escribir 2 deja `totalChars = 4`.
  - Estado: parcial. Backspace ajusta `correctChars`, `incorrectChars` y `totalChars`;
    `handlePaste` no actualiza esos contadores (solo el valor del input), así que las
    estadísticas quedan desfasadas hasta la siguiente pulsación.

- [ ] **T004-11** Extraer `computeWpm()` y `computeAccuracy()` como funciones puras y reutilizarlas.
  - Requisitos: `RF-004-04`, `RF-004-05`
  - Archivos: `script.js`
  - DoD: mismo resultado en vivo y al final; sin duplicar fórmulas.
  - Estado: pendiente. La fórmula de WPM está duplicada en `updateLiveStats` (l. 451)
    y `endTest` (l. 486); la de precisión en l. 459 y l. 491.

- [x] **T004-12** Eliminar el atributo `value=""` del `<textarea>` y añadir `aria-label`.
  - Requisito: `RNF-004-04`
  - Archivos: `templates/index.html`
  - Evidencia: `index.html:125` sin `value=""` y con `aria-label="Typing input"`.

- [ ] **T004-13** Garantizar limpieza de `timerInterval` en fin, reinicio y `blur`.
  - Requisito: `RNF-004-02`
  - Archivos: `script.js`
  - DoD: tras 3 reinicios solo hay un intervalo activo.
  - Estado: parcial. `endTest` y `blur` limpian el intervalo; `restartTest` llama a
    `startTest` sin `clearInterval` previo, por lo que reiniciar durante un test
    activo deja el intervalo anterior vivo.

## Fase 3 — Verificación

- [ ] **T004-14** Ejecutar el checklist manual del `plan.md` y registrar evidencia.
  - Requisitos: `CA-004-01`…`CA-004-09`

- [ ] **T004-15** Decidir el destino de las métricas avanzadas (`spacing`, `duration`, `afkHistory`, `errorHistory`).
  - Requisito: `RF-004-15`
  - Opciones: eliminarlas o exponerlas en un panel de detalles.
  - DoD: documentado en `plan.md` y sin código muerto.

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
