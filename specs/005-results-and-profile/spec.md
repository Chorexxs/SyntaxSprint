# Spec 005 — Resultados, perfil e historial

| Campo | Valor |
| --- | --- |
| Estado | Implementada (backlog en `tasks.md`) |
| Versión | 1.0 |
| Depende de | 002-authentication, 004-typing-engine |
| Archivos principales | `backend/models.py`, `backend/result_views.py`, `templates/profile.html`, `backend/migrations/0001_initial.py` |

## 1. Contexto y problema

El valor del producto está en medir progreso. Cada test genera un resultado que se
guarda y se muestra en el perfil con promedios. Hoy el backend confía ciegamente en los
valores enviados por el cliente, no limita el historial y el guardado falla en silencio
para usuarios anónimos.

## 2. Objetivos

1. Persistir cada resultado con usuario, WPM, precisión y fecha.
2. Mostrar historial ordenado y promedios.
3. Validar los datos en el servidor.
4. Presentar un estado vacío útil.

### No objetivos

- Ranking global o comparación entre usuarios.
- Eliminar o editar resultados desde la UI.
- Exportar a CSV.
- Gráficas históricas (backlog).

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Usuario autenticado | Guardar resultado automáticamente; consultar historial y promedios. |
| Visitante | No puede guardar; se le invita a iniciar sesión. |
| Administrador | Consultar y depurar resultados en admin. |

## 4. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-005-01 | El sistema debe almacenar `user`, `wpm`, `accuracy` y `date` por resultado. | Alta |
| RF-005-02 | Cuando un usuario autenticado envía `{wpm, accuracy}` por POST, el sistema debe crear un resultado. | Alta |
| RF-005-03 | Cuando faltan datos o no son numéricos, el sistema debe responder 400. | Alta |
| RF-005-04 | Cuando el método no es POST, el sistema debe responder 405. | Alta |
| RF-005-05 | Cuando un usuario abre `/profile`, el sistema debe listar sus resultados de más reciente a más antiguo. | Alta |
| RF-005-06 | El perfil debe mostrar el promedio de WPM y de precisión del usuario. | Alta |
| RF-005-07 | Cuando no hay resultados, el perfil debe mostrar un estado vacío con enlace a hacer un test. | Media |
| RF-005-08 | Cuando el usuario no está autenticado, el perfil y el guardado deben redirigir a login. | Alta |
| RF-005-09 | El sistema debe rechazar WPM negativo, accuracy fuera de 0–100 o valores no finitos. | Alta |
| RF-005-10 | El sistema debe limitar el historial mostrado (paginación o top N). | Media |
| RF-005-11 | El perfil debe mostrar la fecha de cada resultado en formato legible. | Media |
| RF-005-12 | El sistema debe eliminar los resultados en cascada al borrar el usuario. | Media |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| `wpm` | Número ≥ 0 y ≤ 400 (límite anti-abuso). |
| `accuracy` | Número entre 0 y 100. |
| `date` | Asignada por el servidor (`auto_now_add`), nunca por el cliente. |
| Usuario | Siempre `request.user`; el cliente no puede elegir otro. |
| Promedios | `Avg()` sobre todos los resultados; 0 si no hay ninguno. |
| Orden | `-date`. |

## 6. Contratos

### Modelo

| Campo | Tipo | Restricciones |
| --- | --- | --- |
| `id` | BigAutoField | PK |
| `user` | FK `auth.User` | `on_delete=CASCADE` |
| `wpm` | FloatField | ≥ 0 (validar en vista) |
| `accuracy` | FloatField | 0–100 (validar en vista) |
| `date` | DateTimeField | `auto_now_add=True` |

### Endpoints

| Método | Ruta | Auth | Entrada | Salida | Errores |
| --- | --- | --- | --- | --- | --- |
| POST | `/save_typing_test_result` | Sí | `{wpm, accuracy}` | `{"message": "Resultado guardado exitosamente"}` | 400 datos inválidos, 405 método |
| GET | `/profile` | Sí | — | HTML con `results`, `avg_wpm`, `avg_accuracy` | 302 a login |

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-005-01 | El guardado debe completarse en < 200 ms en local. |
| RNF-005-02 | El endpoint debe ser idempotente ante doble envío accidental (backlog). |
| RNF-005-03 | Los números deben mostrarse con `floatformat:0` y separador local. |
| RNF-005-04 | La tabla debe ser usable en móvil (scroll horizontal o tarjetas). |

## 8. Criterios de aceptación

- **CA-005-01** Dado un usuario autenticado, cuando envía `{wpm: 60, accuracy: 95}`, entonces se crea un registro y responde 200.
- **CA-005-02** Dado `{wpm: "abc", accuracy: 95}`, entonces responde 400 y no crea nada.
- **CA-005-03** Dado `{wpm: 60, accuracy: 150}`, entonces responde 400.
- **CA-005-04** Dado un GET, entonces responde 405.
- **CA-005-05** Dados dos resultados (60/90 y 80/100), el perfil muestra promedio 70 y 95.
- **CA-005-06** Dado un usuario sin resultados, el perfil muestra "no results yet".
- **CA-005-07** Dado otro usuario, no veo sus resultados (aislamiento por `request.user`).
- **CA-005-08** Al borrar el usuario, sus resultados desaparecen.

## 9. Fuera de alcance

- Edición/borrado de resultados por el usuario.
- Ranking, logros y rachas.
- Comparación con la media global.
- Exportación de datos.

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| WPM/accuracy calculados en cliente | Datos falsificables | Validar rangos; a futuro recalcular en servidor |
| `json.loads` sin `try/except` | 500 con cuerpo inválido | T005-05 |
| Sin paginación | Perfil lento con miles de filas | T005-08 |
| `on_profile_page` en contexto sin uso | Código muerto | T005-08 |
| Promedios en una consulta por métrica | 2 queries | `aggregate(Avg('wpm'), Avg('accuracy'))` |
| Doble envío por reintento | Duplicados | Backlog: token idempotente |

## 11. Referencias de código

- `backend/models.py`
- `backend/views.py` → `save_typing_test_result`, `profile`
- `templates/profile.html`
- `backend/migrations/0001_initial.py`
