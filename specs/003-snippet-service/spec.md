# Spec 003 — Servicio de fragmentos de código

| Campo | Valor |
| --- | --- |
| Estado | Implementada |
| Versión | 1.0 |
| Depende de | 001-foundation |
| Archivos principales | `backend/views.py` → `get_python_function`, `backend/urls.py` |

## 1. Contexto y problema

El test necesita un fragmento de código distinto cada vez, adecuado al lenguaje elegido.
El catálogo vive embebido en la vista y se sirve como JSON. Funciona, pero el nombre del
endpoint (`get_python_function`) ya no refleja que soporta ocho lenguajes y la vista
puede fallar con JSON malformado.

## 2. Objetivos

1. Entregar un fragmento aleatorio por lenguaje.
2. Ofrecer un catálogo suficientemente variado (15 fragmentos por lenguaje).
3. Responder siempre con un contrato estable `{name, code}`.
4. Fallar de forma controlada ante entradas inválidas.

### No objetivos

- Persistir fragmentos en base de datos.
- Editar fragmentos desde el admin.
- Ejecutar o validar el código del fragmento.
- Marcar dificultad o longitud.

## 3. Actores y casos de uso

| Actor | Caso de uso |
| --- | --- |
| Visitante / Usuario | Solicitar un fragmento del lenguaje seleccionado. |
| Motor de test | Consumir `code` para renderizar el prompt. |

## 4. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-003-01 | El sistema debe soportar los lenguajes `python`, `javascript`, `typescript`, `html`, `css`, `sql`, `java` y `go`. | Alta |
| RF-003-02 | Cuando recibe un lenguaje válido, el sistema debe devolver un fragmento aleatorio de ese lenguaje. | Alta |
| RF-003-03 | Cuando recibe un lenguaje desconocido o ausente, el sistema debe devolver un fragmento de Python. | Media |
| RF-003-04 | El sistema debe responder JSON con las claves `name` y `code`. | Alta |
| RF-003-05 | El sistema debe aceptar `POST` con cuerpo JSON `{"language": "..."}` y `GET` sin cuerpo. | Alta |
| RF-003-06 | El sistema debe incluir al menos 15 fragmentos por lenguaje. | Media |
| RF-003-07 | Cuando el cuerpo JSON es inválido, el sistema debe responder 400, no 500. | Alta |
| RF-003-08 | El sistema no debe revelar el catálogo completo en una sola respuesta. | Baja |

## 5. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| Lenguaje válido | `lookup` exacto, case-sensitive (`python`, no `Python`). |
| Lenguaje ausente | `python`. |
| Cuerpo vacío en POST | `python`. |
| Cuerpo no-JSON | responder 400 con `{"error": ...}`. |
| Selección | `random.choice` uniforme sobre la lista del lenguaje. |
| Respuesta | `application/json`, sin caché explícita. |

## 6. Contratos

### `POST /get_python_function`

```json
// Petición
{ "language": "javascript" }

// 200
{ "name": "Arrow Function", "code": "const add = (a, b) => a + b;" }
```

| Método | Ruta | Auth | Errores |
| --- | --- | --- | --- |
| GET | `/get_python_function` | No | 200 |
| POST | `/get_python_function` | No | 400 JSON inválido |

### Lenguajes soportados

| Clave | Etiqueta UI | Fragmentos |
| --- | --- | --- |
| `python` | Python | 15 |
| `javascript` | JavaScript | 15 |
| `typescript` | TypeScript | 15 |
| `html` | HTML | 15 |
| `css` | CSS | 15 |
| `sql` | SQL | 15 |
| `java` | Java | 15 |
| `go` | Go | 15 |

## 7. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-003-01 | Respuesta < 300 ms en local. |
| RNF-003-02 | Catálogo extraído a módulo propio (`backend/snippets.py`) para reducir el tamaño de `views.py`. |
| RNF-003-03 | Validar que todo fragmento tenga `name` y `code` no vacíos. |

## 8. Criterios de aceptación

- **CA-003-01** Dado `{"language": "sql"}`, cuando hago POST, entonces recibo un fragmento SQL con `name` y `code`.
- **CA-003-02** Dado `{"language": "cobol"}`, entonces recibo un fragmento de Python.
- **CA-003-03** Dado un GET, entonces recibo un fragmento de Python.
- **CA-003-04** Dado un cuerpo `no-json`, entonces recibo 400 y el servidor no lanza excepción.
- **CA-003-05** Dado 20 llamadas seguidas, entonces aparecen al menos 3 fragmentos distintos de Python (aleatoriedad).

## 9. Fuera de alcance

- Filtros por longitud o dificultad.
- Favoritos de fragmentos.
- Nuevos lenguajes (Rust, C++, Kotlin) — backlog.

## 10. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| Catálogo dentro de `views.py` (≈145 líneas) | Mantenibilidad | T003-04 |
| Validación solo en cliente | Lenguaje inválido cae a Python silenciosamente | Documentado en RF-003-03 |
| `json.loads` sin `try/except` | 500 ante cuerpo inválido | T003-03 |
| Nombre del endpoint confuso | Deuda de nomenclatura | Mantener por compatibilidad; documentar alias en backlog |

## 11. Referencias de código

- `backend/views.py` líneas 31–181
- `backend/urls.py` línea 6
- `static/js/script.js` → `startTest`, `apiUrl`
