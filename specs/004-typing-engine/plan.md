# Plan técnico 004 — Motor de test de mecanografía

| Campo | Valor |
| --- | --- |
| Spec | `specs/004-typing-engine/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Mantener la clase `TypingTest` como unidad, pero dividir sus responsabilidades en métodos
pequeños y testeables (`computeWpm`, `computeAccuracy`, `resetState`). Corregir el CSRF
de la portada y el manejo de la respuesta de guardado. No se introduce build ni
framework: el archivo sigue siendo un script clásico servido por Django.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `templates/index.html` | Modificar | Añadir `{% csrf_token %}` oculto; quitar `value` del textarea; mensaje accesible. |
| `static/js/script.js` | Modificar | Helpers de cálculo, guardado con manejo de respuesta, limpieza de intervalos. |
| `static/css/styles.css` | Modificar | Añadir estilos de mensaje de error/estado. |
| `backend/views.py` | Modificar | (Coordina con 005) validar y responder JSON siempre. |

## 3. Diseño de estado

```text
Antes:  hero visible · test oculto · results oculto
Test:   hero oculto  · test visible · results oculto
Final:  hero oculto  · test oculto  · results visible
```

Se conserva el objeto `state`, pero los cálculos se extraen:

```javascript
computeWpm(correctChars, elapsedMs) {
  const minutes = elapsedMs / 1000 / 60;
  return minutes > 0 ? Math.round((correctChars / 5) / minutes) : 0;
}

computeAccuracy(correct, incorrect) {
  const total = correct + incorrect;
  return total > 0 ? Math.round((correct / total) * 100) : 100;
}
```

## 4. Secuencia del test

```text
click start
  └─ fetch POST /get_python_function (con X-CSRFToken)
       └─ resetState() ─► renderCode() ─► focus() ─► startTimer()

keydown/input
  └─ actualizar contadores ─► updateDisplay() ─► updateLiveStats()

timer tick (1 s)
  └─ timeLeft-- ─► si 0 → endTest()

endTest()
  └─ clearInterval ─► computeWpm/Accuracy ─► mostrar ─► saveResult()
```

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| Extraer motor a módulo ES (`type="module"`) | Testeable con Vitest | Requiere ajustar `static` y CSP | Backlog |
| Reescribir con React/Vue | Componentes | Añade build y dependencias | No |
| Endpoint GET para snippets | Evita CSRF | Cambia contrato | No (pero aceptable como fallback) |
| Guardar también en `localStorage` | Resiliencia | Duplica fuente de verdad | No |

## 6. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Manual | Flujo completo con y sin sesión | Navegador |
| Manual | Pegado, backspace, flechas, Tab, cambio de pestaña | Navegador |
| Manual | Temas claro/oscuro y responsive 375 px / 1440 px | DevTools |
| Integración | POST de guardado con CSRF | `django.test.Client` |
| Futuro | Cálculos WPM/accuracy | Vitest o tests puros en JS |

Checklist manual mínima:

- [x] Abrir ventana privada, pulsar start → no hay 403.
- [x] Escribir correcto/incorrecto → colores correctos.
- [x] Pegar texto largo → se trunca.
- [x] Dejar correr 30 s → resultados y POST 200.
- [x] Usuario anónimo → mensaje "inicia sesión para guardar".
- [x] Repetir test → fragmento nuevo y contadores a 0.

> Última ejecución: 2026-11-11, Chrome DevTools contra `runserver` local. Resultado
> completo en `T004-14` (`tasks.md`): 6/6 ítems en verde y `CA-004-01`…`CA-004-09`
> verificados. El POST de guardado responde 302 para visitantes (mensaje de sesión) y
> 200 para usuarios autenticados.

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| `python-decouple` + CSRF en tests | Media | `Client(enforce_csrf_checks=True)` en tests dedicados |
| Cambios en contadores rompen WPM | Media | Extraer funciones puras y probarlas |
| `setInterval` sigue tras reinicio | Media | Guardar ID y limpiar en `resetState` |
| Timing distinto en CI | Baja | No testear tiempos reales; inyectar reloj |

## 8. Orden de implementación

1. CSRF en `index.html` (`{% csrf_token %}` dentro de un `div` oculto).
2. Helpers `computeWpm` / `computeAccuracy` y usarlos en `endTest` y `updateLiveStats`.
3. `resetState()` y limpieza de intervalos.
4. Manejo de respuesta de guardado (200/302/403/500).
5. Corregir contadores en backspace/pegado.
6. Checklist manual y documentar resultados.

## 9. Notas de despliegue

- Sin migraciones.
- Invalidar caché de `script.js` (añadir query `?v=` o `ManifestStaticFilesStorage` en 007).
