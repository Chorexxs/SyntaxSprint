# Tareas 000 — Roadmap global

Leyenda: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada
Referencia: `specs/000-overview/spec.md`

## Estado de las funcionalidades

- [x] **T000-01** Definir visión, alcance y glosario del producto.
- [x] **T000-02** Documentar arquitectura y decisiones (ADR-01…ADR-06).
- [x] **T000-03** Crear estructura SDD (`specs/`, plantillas, constitución).
- [x] **T000-04** Inventariar deuda técnica transversal.
- [x] **T000-05** Revisar y aprobar el roadmap con el responsable del proyecto.
  - Evidencia: aprobado por el responsable el 2026-11-11, tras verificar 39 tests,
    cobertura 99 %, CI en verde y sitio en producción. Los milestones M1–M6 quedan
    cerrados; el trabajo futuro vive en el backlog de cada `tasks.md`.
- [x] **T000-06** Definir métricas de éxito medibles en analítica (requiere 007).
  - Evidencia: cumplida por `specs/011-analytics`. `manage.py analytics_report` mide
    tests por usuario y semana, error rate de `/get_python_function` y porcentaje de
    registrados con resultado; `purge_analytics` aplica la retención de 90 días.
    Lighthouse queda como medición externa documentada.
- [x] **T000-07** Definir el procedimiento de auditoría de código (spec 008).
- [x] **T000-08** Definir el procedimiento de auditoría de seguridad (spec 009).
- [x] **T000-09** Definir el procedimiento de actualización de dependencias (spec 010).

> No quedan tareas abiertas en el roadmap. El trabajo futuro vive en el backlog de cada
> `tasks.md` y en specs nuevas.

## Milestones

| Milestone | Contenido | Estado |
| --- | --- | --- |
| **M1 — Documentación** | specs 000–007, AGENTS.md, trazabilidad | [x] |
| **M2 — Red de seguridad** | Tests de auth, snippets y resultados (007 fase 1) | [x] |
| **M3 — Correcciones funcionales** | CSRF en portada, validación de resultados, redirects de login | [x] |
| **M4 — Accesibilidad y UI** | Nombres accesibles, contraste, deduplicar tema | [x] |
| **M5 — Producción** | Settings seguros, CI, estáticos, README alineado | [x] |
| **M6 — Gobernanza** | Auditorías de código y seguridad bajo demanda + línea base | [x] |

> Evidencia de M2–M5 (2026-11-11): 39 tests en verde, cobertura del backend 99 %,
> `pylint` 10.00/10, CI en `.github/workflows/ci.yml`, WhiteNoise + `render.yaml` y
> sitio en producción. Tareas: T007-01…T007-22, T002-07/T002-09, T005-05, T006-05…T006-08.

## Mapa de dependencias entre funcionalidades

```text
001-foundation
   ├── 002-authentication
   ├── 003-snippet-service
   │      └── 004-typing-engine
   │             └── 005-results-and-profile
   └── 006-ui-and-theming
             └── 007-quality-and-delivery (transversal)

008-code-audit      ── transversal (calidad)
009-cybersecurity   ── transversal (seguridad)
```

## Orden de ejecución sugerido (sprints de 1 semana)

| Sprint | Objetivo | Tareas |
| --- | --- | --- |
| S1 | Limpieza de base y modelo en admin | T001-03…T001-07 |
| S2 | Pruebas de comportamiento actual | T007-01…T007-04 |
| S3 | Endurecer autenticación y resultados | T002-06…T002-10, T005-05…T005-08 |
| S4 | Corregir CSRF y motor | T004-08…T004-12 |
| S5 | Accesibilidad y temas | T006-05…T006-08 |
| S6 | CI, seguridad y despliegue | T007-05…T007-11 |

## Riesgos del roadmap

| Riesgo | Mitigación |
| --- | --- |
| El alcance crece sin specs | Toda idea nueva entra como `specs/008+` antes de codificarse |
| Refactor grande sin tests | S2 antes de tocar lógica |
| Cambios de despliegue rompen producción | Checklist de `007` y rollback documentado |

## Historial

| Fecha | Cambio |
| --- | --- |
| 2026-11-10 | Creación del roadmap y estructura SDD |
| 2026-11-11 | Cierre de M2–M5 con evidencia verificada; T000-05 y T000-06 quedan abiertas |
| 2026-11-11 | T000-05 aprobada por el responsable; solo queda T000-06 (analítica) |
| 2026-11-11 | T000-06 cerrada con la spec 011: comandos de métricas y purga |
