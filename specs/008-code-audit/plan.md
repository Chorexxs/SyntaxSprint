# Plan técnico 008 — Auditoría de código y arquitectura

| Campo | Valor |
| --- | --- |
| Spec | `specs/008-code-audit/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

La auditoría es un **proceso**, no una funcionalidad de producto. Se apoya en tres
piezas: un medidor determinista (`code_metrics.py`), los verificadores ya instalados
(`pylint`, `isort`, `manage.py`) y una rúbrica de 8 dimensiones con pesos fijos. El
resultado se materializa en un informe markdown versionado para poder comparar
tendencias.

## 2. Artefactos

| Artefacto | Propósito | Acción |
| --- | --- | --- |
| `specs/tools/code_metrics.py` | Métricas objetivas de Python y señales de JS | Creado |
| `specs/templates/audit-report.md` | Formato homogéneo del informe | Creado |
| `audits/code/` | Histórico de auditorías | Creado |
| `specs/008-code-audit/tasks.md` | Seguimiento de la deuda detectada | Creado |

## 3. Decisiones de diseño

| ID | Decisión | Motivo | Consecuencia |
| --- | --- | --- | --- |
| ADR-008-01 | Herramienta propia con `ast` y sin dependencias | Funciona en cualquier entorno y no añade paquetes | Cobertura limitada a lo modelado |
| ADR-008-02 | Umbrales fijos en el spec | Comparabilidad entre auditorías | Requiere revisión si el proyecto crece |
| ADR-008-03 | Solo lectura durante la auditoría | Evita mezclar diagnóstico y remedio | La corrección va en tareas aparte |
| ADR-008-04 | Informe en `audits/code/` | Historial y diff entre fechas | Hay que mantenerlo actualizado |
| ADR-008-05 | Puntuación ponderada | Prioriza arquitectura y escalabilidad | La nota no refleja un único archivo |

## 4. Modelo de puntuación

```text
score = 0.20*D1 + 0.20*D2 + 0.15*D3 + 0.15*D4 + 0.10*D5 + 0.10*D6 + 0.05*D7 + 0.05*D8
```

| Dimensión | Evidencia principal |
| --- | --- |
| D1 Arquitectura | Lectura de `views.py`, `urls.py`, plantillas; tamaño de funciones |
| D2 Escalabilidad | Consultas, paginación, configuración, acoplamiento del catálogo |
| D3 Legibilidad | `code_metrics.py`, `pylint`, duplicación |
| D4 Errores | Revisión de endpoints y validaciones |
| D5 Testabilidad | `manage.py test`, cobertura |
| D6 Rendimiento | `connection.queries`, `EXPLAIN`, medición manual |
| D7 Frontend | `code_metrics.py` sobre `.js`, revisión de listeners |
| D8 Dependencias/docs | `requirements.txt`, `isort`, README vs código |

## 5. Flujo de ejecución

```text
Disparador del usuario
  └─ 0. git status + commit
     1. code_metrics + check + test + isort + pylint
     2. Revisión manual D1…D8 (checklist del spec)
     3. Clasificación y score
     4. Informe en audits/code/AAAA-MM-DD-alcance.md
     5. Tareas/specs derivadas + traceability
```

## 6. Reglas de evidencia

Un hallazgo es válido solo si cumple **una** de estas condiciones:

1. Comando reproducible + salida (p. ej. `pylint` con código y línea).
2. Cita literal de `archivo:línea` con el fragmento mínimo.
3. Medición con número y método (p. ej. 7 queries en `profile`).

No se aceptan impresiones sin evidencia. Los falsos positivos se marcan `[FP]` y se
explican.

## 7. Estrategia de verificación

| Nivel | Qué se prueba | Cómo |
| --- | --- | --- |
| Unitario | El medidor detecta funciones largas y anidamiento | Casos de prueba manuales con un archivo temporal |
| Integración | El procedimiento completo produce informe | Ejecución real de la línea base |
| Consistencia | Todo hallazgo tiene tarea | Revisión cruzada con `tasks.md` |
| Tendencia | El score cambia con las correcciones | Comparar informes |

## 8. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| `pylint` sin `pylint-django` da falsos `no-member` | Alta | Cargar el plugin y el settings module |
| `code_metrics` cuenta funciones anidadas dos veces | Media | Documentado como aproximación; usar `pylint` como contraste |
| El informe se vuelve un refactor | Media | Separar auditoría (solo lectura) de remediación |
| Scores incomparables por cambio de umbrales | Baja | Versionar los umbrales en el spec |

### Comando de pylint recomendado

```bash
cd syntax_sprint
python -m pylint backend syntax_sprint \
  --load-plugins=pylint_django \
  --django-settings-module=syntax_sprint.settings \
  --score=y
```

Requiere `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` en el entorno.

## 9. Orden de implementación

1. Publicar el procedimiento y la rúbrica (hecho).
2. Publicar el medidor y la plantilla (hecho).
3. Ejecutar la línea base y guardarla (hecho parcial).
4. Derivar tareas de los hallazgos ALTA.
5. Repetir tras cada bloque grande de cambios.

## 10. Notas de operación

- No se ejecuta en CI por defecto; consume tiempo y es subjetivo.
- Sí se pueden ejecutar `pylint`, `isort` y `code_metrics` en CI como *quality gate*
  objetivo (ver `007`).
- Los informes se guardan en git para conservar la tendencia.
