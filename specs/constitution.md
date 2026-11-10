# Constitución técnica de SyntaxSprint

Reglas no negociables. Cualquier cambio que las viole debe justificarse por escrito en
el `plan.md` de la funcionalidad correspondiente.

## Artículo 1 — La especificación manda

1. Todo comportamiento observable del sistema debe estar descrito por un requisito
   (`RF-*`) con al menos un criterio de aceptación.
2. Si la implementación y la especificación difieren, la especificación es la
   intención y la implementación es el defecto, salvo que la spec se actualice
   explícitamente en el mismo cambio.
3. No se aceptan "arreglos rápidos" sin tarea asociada.

## Artículo 2 — Simplicidad primero

1. Se mantiene la arquitectura **Django MVT + JavaScript vanilla**. No se introduce
   SPA, framework frontend ni API REST completa sin una spec aprobada.
2. jQuery solo se usa si ya está presente en la página; el motor de typing usa
   JavaScript moderno (ES6+) con clases y `fetch`.
3. Prohibido añadir dependencias que no resuelvan un requisito concreto.
4. La lógica de negocio vive en `backend/`; las plantillas solo presentan datos.

## Artículo 3 — Contratos estables

1. Las URLs existentes son parte del contrato público y **no se renombran** sin
   redirección de compatibilidad.
2. Los endpoints JSON mantienen la forma de respuesta documentada en `plan.md`.
3. Las migraciones son **solo hacia adelante**; nunca se edita una migración ya
   aplicada en producción.
4. Todo cambio de modelo requiere su migración en el mismo commit.

## Artículo 4 — Seguridad por defecto

1. Ningún secreto se versiona. `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` se leen de
   `.env` mediante `python-decouple`.
2. `DEBUG` debe ser `False` en producción.
3. Toda vista que modifica datos exige autenticación y protección CSRF.
4. Los datos del usuario se validan en el servidor; la validación del cliente es
   solo experiencia de usuario.
5. Los errores internos se registran, nunca se devuelven al usuario.

## Artículo 5 — Calidad verificable

1. Cada vista nueva tiene al menos una prueba de camino feliz y una de error.
2. `python manage.py check` y la suite de pruebas deben pasar antes de integrar.
3. Se respeta `isort` (stdlib → terceros → Django → locales) y `pylint`.
4. Máximo 100 caracteres por línea, 4 espacios de indentación, sin espacios finales.
5. Se usan anotaciones de tipo en funciones nuevas de Python.

## Artículo 6 — Accesibilidad y rendimiento

1. Todo control interactivo debe ser alcanzable por teclado y tener nombre accesible.
2. El contraste de texto debe cumplir WCAG AA en ambos temas.
3. El test debe funcionar sin conexión a servicios externos salvo el propio backend.
4. El tiempo de carga del test no debe superar 2 s en una conexión normal.

## Artículo 7 — Documentación viva

1. `README.md`, `AGENTS.md` y `specs/` describen el estado real del proyecto.
2. Toda decisión relevante (trade-off, deuda aceptada) se registra en el `plan.md`.
3. Las tareas completadas permanecen en `tasks.md` como historial; no se borran.

## Artículo 8 — Flujo de cambios

1. Una rama por funcionalidad (`feature/<nombre>`), un commit atómico por tarea.
2. **Los mensajes de commit se escriben siempre en español**, en imperativo y
   describiendo el qué y el porqué. Formato: `Tipo: descripción`
   (ver la sección de commits de `AGENTS.md`).
3. Ningún commit mezcla refactor, funcionalidad y formato.
4. Antes de fusionar: DoD cumplido y `traceability.md` actualizado.
