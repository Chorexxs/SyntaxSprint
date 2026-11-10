# Spec 004 — Motor de test de mecanografía

| Campo | Valor |
| --- | --- |
| Estado | Implementada (con deuda) |
| Versión | 1.0 |
| Depende de | 003-snippet-service |
| Archivos principales | `static/js/script.js`, `templates/index.html`, `static/css/styles.css` |

## 1. Contexto y problema

Es el corazón del producto: el usuario escribe un fragmento de código durante 30 segundos
y recibe su WPM y precisión. La implementación actual (clase `TypingTest`, 550 líneas)
funciona, pero carece de pruebas, tiene lógica de tracking que no se usa, depende de que
el CSRF esté inicializado y no informa al usuario si el guardado falla.

## 2. Objetivos

1. Medir WPM y precisión de forma consistente y explicable.
2. Dar feedback en tiempo real (temporizador, WPM y precisión en vivo).
3. Evitar trampas básicas (pegar texto, atajos, autocompletado).
4. Permitir repetir el test con un fragmento nuevo.
5. Guardar el resultado al finalizar si el usuario está autenticado.

### No objetivos

- Modos de test (tiempo configurable, palabras, cita) — backlog.
- Historial de pulsaciones visible.
- Sonidos o efectos de audio.
- Corrección ortográfica o linting del código escrito.

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Visitante | Elegir lenguaje, iniciar test, ver resultado (sin guardar). |
| Usuario autenticado | Igual, y su resultado queda registrado en el perfil. |

## 4. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-004-01 | Cuando el usuario pulsa "start", el sistema debe pedir un fragmento del lenguaje seleccionado y mostrar el área de test. | Alta |
| RF-004-02 | El sistema debe iniciar un temporizador de 30 segundos al comenzar el test. | Alta |
| RF-004-03 | El sistema debe renderizar el fragmento carácter a carácter con estados pendiente/correcto/incorrecto/activo. | Alta |
| RF-004-04 | El sistema debe calcular WPM como `(caracteres correctos / 5) / minutos transcurridos`. | Alta |
| RF-004-05 | El sistema debe calcular precisión como `correctos / (correctos + incorrectos) × 100`. | Alta |
| RF-004-06 | El sistema debe actualizar WPM y precisión en vivo cada segundo y en cada pulsación. | Media |
| RF-004-07 | Cuando el usuario pega texto, el sistema debe insertarlo limitado a la longitud restante y recalcular. | Alta |
| RF-004-08 | Cuando el usuario pulsa Backspace, el sistema debe retroceder un carácter y ajustar contadores. | Alta |
| RF-004-09 | El sistema debe bloquear Enter, Escape, Tab (salvo foco) y flechas durante el test. | Media |
| RF-004-10 | El sistema debe finalizar el test al llegar a 0 s o al completar el fragmento. | Alta |
| RF-004-11 | Cuando el test termina, el sistema debe mostrar resultados y permitir "try again". | Alta |
| RF-004-12 | Cuando el usuario está autenticado, el sistema debe enviar WPM y precisión a `/save_typing_test_result`. | Alta |
| RF-004-13 | El sistema debe soportar IME sin contar composiciones intermedias. | Media |
| RF-004-14 | El sistema debe pausar el temporizador si la ventana pierde el foco. | Media |
| RF-004-15 | El sistema debe registrar métricas avanzadas (spacing, duración, AFK, errores) sin afectar el resultado. | Baja |
| RF-004-16 | El sistema debe recordar el tema claro/oscuro en `localStorage`. | Media |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| Espacio inicial | Se ignora si el input está vacío. |
| Carácter extra | El input no puede superar la longitud del fragmento. |
| Comparación | Exacta, case-sensitive y con espacios/saltos de línea. |
| Backspace | Solo elimina el último carácter; no permite editar en medio. |
| Atajos | Ctrl/Cmd, F1–F12, Alt, Shift, Meta y bloqueos se ignoran. |
| Fin por tiempo | `timeLeft <= 0`. |
| Fin por longitud | `typedLength >= currentCode.length`. |
| Visitante | Intenta guardar; el backend responde redirección y el error se registra en consola. |

## 6. Contratos

### Estado interno

```text
TypingTest.state
├── active, testTime, timeLeft
├── currentCode, startTime, timerInterval
├── language, isComposing, isFocused
├── correctChars, incorrectChars, totalChars
├── spacing { first, last, array }
├── duration { array }
├── keyDownData {}, keyOverlap { total }
├── currentAfk, afkHistory [], errorHistory [], isInError
```

### Endpoints consumidos

| Método | Ruta | Cuerpo | Respuesta |
| --- | --- | --- | --- |
| POST | `/get_python_function` | `{ language }` | `{ name, code }` |
| POST | `/save_typing_test_result` | `{ wpm, accuracy }` | `{ message }` |

### Funciones públicas de la clase

| Método | Responsabilidad |
| --- | --- |
| `init()` | Registrar listeners e inicializar tema. |
| `startTest()` | Cargar fragmento, resetear estado, arrancar timer. |
| `endTest()` | Calcular resultado, mostrar y guardar. |
| `restartTest()` | Limpiar resultados y relanzar `startTest`. |
| `saveResult(wpm, acc)` | POST al backend. |

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-004-01 | Sin jQuery: ES6+ nativo. |
| RNF-004-02 | Sin fugas de intervalos: `clearInterval` en `endTest`, `blur` y reinicio. |
| RNF-004-03 | El DOM no debe re-renderizarse completo en cada tecla (solo clases). |
| RNF-004-04 | Accesible por teclado y con instrucciones visibles. |
| RNF-004-05 | Tolerante a fallos de red: el test debe completarse aunque el guardado falle. |

## 8. Criterios de aceptación

- **CA-004-01** Dado un visitante en `/`, cuando pulsa "start", entonces ve el fragmento y el temporizador en 30.
- **CA-004-02** Dado el test activo, cuando escribe 5 caracteres correctos en 1 minuto, entonces WPM = 1.
- **CA-004-03** Dado 10 caracteres escritos con 8 correctos, entonces la precisión es 80 %.
- **CA-004-04** Dado un carácter incorrecto, entonces se pinta en rojo y la precisión baja.
- **CA-004-05** Dado el test activo, cuando pega 200 caracteres, entonces solo se aceptan los que caben.
- **CA-004-06** Cuando el temporizador llega a 0, entonces se muestran resultados y se envía el POST.
- **CA-004-07** Dado el test terminado, cuando pulsa "try again", entonces recibe un fragmento nuevo.
- **CA-004-08** Dado un usuario autenticado, tras terminar el test el resultado aparece en `/profile`.
- **CA-004-09** Dado el test activo, cuando cambia de pestaña, el temporizador se pausa.

## 9. Fuera de alcance

- Modo "zen", "quote" o "words".
- Tests de más de 30 s configurables.
- Guardado offline o reintento automático.
- Gráficas de progreso (ver backlog de 005).

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| `index.html` no renderiza `{% csrf_token %}` | El POST de inicio puede dar 403 en sesión nueva | T004-08 |
| `saveResult` ignora la respuesta | El usuario cree que guardó y no fue así | T004-09 |
| Métricas avanzadas se calculan y no se usan | Complejidad muerta | T004-11 o eliminarlas |
| `handleInput` usa `prevLength = totalChars` | Backspace y pegado pueden desincronizar contadores | T004-10 |
| Timer depende de `setInterval` (deriva) | WPM impreciso en tests largos | Calcular con `Date.now()` (ya usado en WPM) |
| `textarea` con atributo `value` | HTML inválido | T004-12 |
| Sin tests de frontend | Regresiones invisibles | Backlog (Vitest/Playwright) |

## 11. Referencias de código

- `static/js/script.js` (clase `TypingTest`, listeners al final)
- `templates/index.html` (IDs, `apiUrl`, `saveResultUrl`)
- `static/css/styles.css` (estados `letter`)
