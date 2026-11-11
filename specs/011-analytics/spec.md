# Spec 011 — Analítica de producto

| Campo | Valor |
| --- | --- |
| Estado | Implementada |
| Versión | 1.0 |
| Depende de | 000-overview, 003-snippet-service, 005-results-and-profile, 007-quality-and-delivery |
| Archivos principales | `backend/models.py`, `backend/analytics.py`, `backend/snippet_views.py`, `backend/management/commands/`, `backend/admin.py` |

## 1. Contexto y problema

`specs/000-overview/spec.md` §7 fija cuatro métricas de éxito: tests por usuario y semana,
error rate de la API de fragmentos, porcentaje de registrados que guardan un resultado y
Lighthouse ≥ 90. Hoy no existe instrumentación: el sistema no registra el resultado de las
peticiones a `/get_python_function`, así que no puede responder con datos a esas preguntas.
La tarea `T000-06` exige medirlas.

## 2. Objetivos

1. Registrar cada petición a `/get_python_function` con su resultado y duración.
2. Calcular en un comando las tres métricas que dependen de datos propios.
3. Medir sin datos personales, sin cookies de terceros y sin dependencias nuevas.
4. Poder purgar los eventos antiguos y consultarlos desde el admin.

### No objetivos

- Panel gráfico, embudos, mapas de calor o atribución de campañas.
- Lighthouse: se mide con la herramienta externa y se documenta el comando.
- Analítica de navegación (páginas vistas, referrers, dispositivos).
- Banner de consentimiento: al no haber cookies de analítica, no aplica.

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Responsable del proyecto | Ejecutar `analytics_report`, leer las métricas y purgar eventos antiguos. |
| Administrador | Consultar los eventos registrados en `/admin/` en solo lectura. |
| Visitante y usuario | No interactúan con la analítica; su experiencia no cambia. |

## 4. Requisitos funcionales

> Formato EARS: *Cuando* <evento>, *el sistema debe* <comportamiento>.

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-011-01 | Cuando se atiende una petición a `/get_python_function`, el sistema debe registrar el lenguaje, el código HTTP, la duración en milisegundos y si hubo error. | Alta |
| RF-011-02 | Cuando el registro del evento falle por un error de base de datos, el sistema debe responder la petición con normalidad y anotar el fallo en el log. | Alta |
| RF-011-03 | Cuando el responsable ejecute `manage.py analytics_report`, el sistema debe mostrar las métricas de la ventana indicada (`--days`, por defecto 28). | Alta |
| RF-011-04 | Cuando el responsable ejecute `manage.py purge_analytics --days N`, el sistema debe eliminar los eventos anteriores a N días (90 por defecto) y rechazar N < 1. | Media |
| RF-011-05 | El administrador debe poder consultar los eventos en `/admin/` sin poder añadirlos ni editarlos. | Media |
| RF-011-06 | Cuando no haya datos en la ventana, el informe debe indicar "sin datos" y terminar con código 0. | Media |
| RF-011-07 | El evento nunca debe contener IP, user-agent, email ni identificadores de usuario. | Alta |
| RF-011-08 | El sistema debe purgar los eventos caducados como máximo una vez al día, sin depender de un cron externo. | Media |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento esperado |
| --- | --- |
| Ventana por defecto | 28 días (4 semanas). |
| Usuario activo | Usuario no-staff con al menos un `TypingTestResult` dentro de la ventana. |
| Tests por usuario y semana | `resultados / usuarios activos / (días / 7)`, redondeado a 2 decimales. |
| Error rate de fragmentos | `peticiones con status ≥ 400 / total de peticiones × 100`, redondeado a 2 decimales. |
| Registrados con resultado | `usuarios no-staff con ≥ 1 resultado / usuarios no-staff × 100`, redondeado a 2 decimales. |
| Lenguaje desconocido | Se registra el lenguaje solicitado (recortado a 32 caracteres); el endpoint mantiene el fallback a Python de `RF-003-03`. |
| Retención | 90 días por defecto; la purga se ejecuta como máximo una vez al día al registrar un evento y también a mano. |
| Lighthouse | Fuera del informe: se mide con Lighthouse CLI sobre la portada. |

## 6. Contratos

### Comandos

| Comando | Entrada | Salida |
| --- | --- | --- |
| `python manage.py analytics_report` | `--days N` (opcional, 28) | Tabla de métricas y objetivos por pantalla |
| `python manage.py purge_analytics` | `--days N` (opcional, 90) | `N eventos eliminados` |

### Modelo de datos

`SnippetRequest`

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `created_at` | `DateTimeField` | `auto_now_add`, indexado |
| `language` | `CharField(max_length=32)` | `"unknown"` si el payload no es válido |
| `status_code` | `PositiveSmallIntegerField` | indexado |
| `duration_ms` | `PositiveIntegerField` | ≥ 0 |

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-011-01 | Sin dependencias nuevas: solo Django y su ORM. |
| RNF-011-02 | El registro añade como máximo una inserción por petición y nunca bloquea la respuesta. |
| RNF-011-03 | Debe funcionar igual en SQLite (pruebas) y PostgreSQL (producción). |
| RNF-011-04 | El informe usa agregaciones de la base de datos, sin cargar eventos en memoria. |
| RNF-011-05 | Sin datos personales: ni IP, ni user-agent, ni email, ni FK a usuario. |

## 8. Criterios de aceptación

- **CA-011-01** Dado un POST válido, cuando responde, entonces existe un evento con status 200, `language = "python"` y `duration_ms ≥ 0`.
- **CA-011-02** Dado un cuerpo JSON inválido, cuando responde 400, entonces el evento tiene status 400 y `language = "unknown"`.
- **CA-011-03** Dado un fallo de base de datos al crear el evento, cuando se pide un fragmento, entonces la respuesta sigue siendo 200 y el fallo queda en el log.
- **CA-011-04** Dadas 2 peticiones con 1 error, entonces el error rate es 50 %.
- **CA-011-05** Dados 2 usuarios y 8 resultados en 28 días, entonces hay 1.0 test por usuario y semana.
- **CA-011-06** Dados 4 usuarios no-staff y 1 con resultado, entonces el porcentaje es 25 %.
- **CA-011-07** Dada una ventana sin datos, entonces el informe muestra "sin datos" y sale con código 0.
- **CA-011-08** Dados eventos antiguos y recientes, cuando se ejecuta `purge_analytics --days 90`, entonces borra los antiguos y conserva los recientes.
- **CA-011-09** Dado el admin, cuando se abre `SnippetRequest`, entonces no ofrece añadir ni editar.
- **CA-011-10** Dado `{"language": "cobol"}`, cuando responde 200 con un fragmento de Python, entonces el evento guarda `language = "cobol"`.
- **CA-011-11** Dado un evento de más de 90 días, cuando se registra una petición, entonces se elimina en la purga diaria y una segunda petición del día no vuelve a purgar.

## 9. Fuera de alcance

- Métricas en tiempo real o panel web público.
- Segmentación por navegador, país o dispositivo.
- Integración con servicios externos de analítica.
- Alertas automáticas cuando una métrica incumple su objetivo.

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Crecimiento de la tabla | Espacio y consultas lentas | Retención de 90 días con `purge_analytics`. |
| Escritura extra por petición | Latencia del endpoint | Una sola inserción, `fail-open` y duración medida. |
| Datos sesgados por bots | Métricas engañosas | No se guarda user-agent; se documenta la limitación. |
| Migración en producción | Despliegue fallido | Migración aditiva y reversible; se aplica con `migrate` en el arranque. |

## 11. Referencias de código

- `backend/models.py` → `SnippetRequest`
- `backend/analytics.py` → registro y cálculo de métricas
- `backend/snippet_views.py` → instrumentación del endpoint
- `backend/management/commands/analytics_report.py`, `purge_analytics.py`
- `backend/admin.py` → vista de solo lectura
- `specs/000-overview/spec.md` §7 — métricas de éxito
