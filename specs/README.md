# Spec-Driven Development (SDD) — SyntaxSprint

Este directorio es la **fuente de verdad** del proyecto. Ningún cambio de código se
considera terminado si no está respaldado por un requisito (`RF-*`), un plan técnico y
una tarea (`T*`) marcada como completada.

## 1. Estructura

```text
specs/
├── README.md                  # Este documento: cómo trabajar con SDD
├── constitution.md            # Principios y restricciones no negociables
├── traceability.md            # Matriz requisito → plan → tarea → prueba
├── templates/                 # Plantillas para nuevas funcionalidades
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── 000-overview/              # Visión de producto y arquitectura global
│   ├── spec.md
│   ├── plan.md
│   └── tasks.md
├── 001-foundation/            # Configuración Django, entorno, estáticos, admin
├── 002-authentication/        # Registro, login, logout, sesiones
├── 003-snippet-service/       # API de fragmentos de código
├── 004-typing-engine/         # Motor de typing test (frontend)
├── 005-results-and-profile/   # Persistencia de resultados e historial
├── 006-ui-and-theming/        # Sistema visual, temas, responsividad
└── 007-quality-and-delivery/  # Pruebas, lint, seguridad, despliegue
```

Cada carpeta de funcionalidad contiene exactamente tres documentos:

| Archivo | Pregunta que responde | Audiencia |
| --- | --- | --- |
| `spec.md` | **¿Qué** debe hacer y **por qué**? | Producto / cualquier persona |
| `plan.md` | **¿Cómo** se implementa técnicamente? | Desarrollo |
| `tasks.md` | **¿En qué orden** y **qué falta**? | Desarrollo / agentes |

## 2. Ciclo de trabajo

1. **Especificar** — Crear o actualizar `spec.md` con requisitos numerados
   (`RF-00X-NN`) y criterios de aceptación. Sin código todavía.
2. **Planificar** — Escribir `plan.md`: archivos afectados, contratos, datos,
   alternativas y estrategia de pruebas.
3. **Descomponer** — Añadir tareas atómicas en `tasks.md` con su *Definition of Done*.
4. **Implementar** — Una tarea a la vez. Cada tarea referencia el requisito que satisface.
5. **Verificar** — Ejecutar pruebas y checklist. Marcar `[x]` y actualizar
   `traceability.md`. Si cambia el alcance, **primero** se actualiza la spec.

## 3. Convenciones

- **IDs de requisito:** `RF-<funcionalidad>-<número>` (ej. `RF-002-05`).
- **IDs de requisito no funcional:** `RNF-<funcionalidad>-<número>`.
- **IDs de tarea:** `T<funcionalidad>-<número>` (ej. `T002-05`).
- **Criterios de aceptación:** `CA-<funcionalidad>-<número>`.
- **Estados de tarea:** `[ ]` pendiente, `[x]` completada, `[!]` bloqueada.
- **Estados de spec:** `Borrador`, `Aprobada`, `Implementada`, `Obsoleta`.
- Los identificadores de código (modelos, vistas, URLs) se escriben en inglés.
  La documentación y los mensajes al usuario, en español.

## 4. Definition of Ready (DoR)

Una funcionalidad puede empezar a implementarse cuando:

- [ ] Existe `spec.md` aprobada por el responsable del proyecto.
- [ ] Todos los requisitos tienen criterios de aceptación verificables.
- [ ] Existe `plan.md` con los archivos que se van a tocar.
- [ ] Las tareas están descompuestas y ordenadas por dependencia.
- [ ] Los riesgos de seguridad y migración están identificados.

## 5. Definition of Done (DoD)

- [ ] Todas las tareas de la funcionalidad están en `[x]`.
- [ ] `python manage.py check` sin errores.
- [ ] `python manage.py test` en verde (o checklist manual documentado si es UI).
- [ ] `isort --check-only syntax_sprint/` y `pylint syntax_sprint/` sin errores nuevos.
- [ ] `spec.md` y `plan.md` reflejan la implementación real.
- [ ] `traceability.md` actualizado.
- [ ] Sin secretos, credenciales ni `DEBUG=True` en el repositorio.

## 6. Cómo añadir una funcionalidad nueva

```text
specs/008-nombre-funcionalidad/
├── spec.md    # copiado de specs/templates/spec.md
├── plan.md    # copiado de specs/templates/plan.md
└── tasks.md   # copiado de specs/templates/tasks.md
```

Después de crearla, añádela a la tabla de `specs/000-overview/spec.md` y a
`specs/traceability.md`.

## 7. Comandos de referencia

```bash
# Desde la raíz del repositorio
cd syntax_sprint

python manage.py check
python manage.py test
python manage.py runserver

isort --check-only .
pylint .
```

## 8. Reglas para agentes de IA

1. Leer `specs/000-overview/spec.md` y la carpeta de la funcionalidad antes de editar.
2. No implementar nada que no esté en una `spec.md`.
3. No marcar una tarea `[x]` sin haber ejecutado su verificación.
4. Si el código y la spec divergen, **detente** y reporta la divergencia.
5. Mantener el estilo y las dependencias existentes; cualquier dependencia nueva
   requiere un requisito explícito.
