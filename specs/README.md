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
│   ├── tasks.md
│   └── audit-report.md        # Plantilla de informes de auditoría
├── tools/                     # Herramientas de verificación sin dependencias
│   ├── code_metrics.py        # Métricas de calidad y complejidad
│   ├── check_dependencies.py  # Inventario y coherencia de dependencias
│   └── scan_secrets.py        # Escáner de secretos y archivos sensibles
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
├── 007-quality-and-delivery/  # Pruebas, lint, seguridad, despliegue
├── 008-code-audit/            # Auditoría de código y arquitectura bajo demanda
├── 009-cybersecurity/         # Auditoría de seguridad y filtraciones bajo demanda
└── 010-dependencies/          # Actualización de dependencias bajo demanda
```

Los informes generados por las auditorías viven fuera de `specs/`:

```text
audits/
├── code/                      # Un informe por auditoría de código
└── security/                  # Un informe por auditoría de seguridad
```
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

## 9. Auditorías bajo demanda

Las auditorías **no se ejecutan solas**: se activan cuando el usuario lo indica.

| Si el usuario dice… | Ejecutar |
| --- | --- |
| "audita el código", "revisa la arquitectura", "¿esto es espagueti?" | `specs/008-code-audit/spec.md` |
| "audita la seguridad", "revisa filtraciones", "¿hay API keys?" | `specs/009-cybersecurity/spec.md` |
| "revisa las dependencias", "actualiza las dependencias" | `specs/010-dependencies/spec.md` |

Reglas comunes:

1. **Solo lectura**: las auditorías (008 y 009) no modifican código; los arreglos van en
   tareas aparte. La actualización de dependencias (010) es la excepción: sí modifica
   `requirements.txt`, siempre en rama y commit propios.
2. **Evidencia obligatoria**: cada hallazgo lleva `archivo:línea` o comando reproducible.
3. **Nunca imprimir secretos**: usar `<redacted>`; ni en el chat ni en el informe.
4. **Informe versionado** en `audits/<tipo>/AAAA-MM-DD-<alcance>.md`.
5. **Trazabilidad**: cada hallazgo se convierte en tarea (`T*`) o en un spec nuevo.
6. **Idioma**: el informe se escribe en español.

Herramientas disponibles:

```bash
python specs/tools/code_metrics.py
python specs/tools/scan_secrets.py
python specs/tools/scan_secrets.py --history
python specs/tools/check_dependencies.py --strict
```
