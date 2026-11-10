# Actualización de dependencias — 2026-11-10

| Campo | Valor |
| --- | --- |
| Fecha | 2026-11-10 |
| Commit de partida | `2ef9f18` |
| Alcance | Python (prod y dev), CDN de frontend, runtime, acciones de CI |
| Procedimiento | `specs/010-dependencies/spec.md` |
| Resultado | Sin vulnerabilidades; parches y menores aplicados |

## 1. Motivo

Primera ejecución del procedimiento `010`. Se buscaba cerrar la deuda detectada en el
inventario inicial: desarrollo y producción mezclados, dependencias sin uso y un CDN sin
versión fija.

## 2. Inventario y acciones

### 2.1 Producción

| Paquete | Antes | Después | Última | Tipo | Acción |
| --- | --- | --- | --- | --- | --- |
| `Django` | 5.2.17 | **5.2.19** | 6.1.3 | Parche / mayor | Parche aplicado; mayor pendiente |
| `dj-database-url` | 3.1.2 | 3.1.2 | 3.1.2 | — | Sin cambio |
| `gunicorn` | 25.3.0 | 25.3.0 | 27.0.0 | Mayor | Pendiente de aprobación |
| `psycopg[binary]` | 3.3.8 | 3.3.8 | 3.3.8 | — | Sin cambio |
| `python-decouple` | 3.8 | 3.8 | 3.8 | — | Sin cambio |
| `whitenoise` | 6.12.0 | 6.12.0 | 6.12.0 | — | Sin cambio |

### 2.2 Desarrollo (nuevo `requirements-dev.txt`)

| Paquete | Antes | Después | Última | Tipo | Acción |
| --- | --- | --- | --- | --- | --- |
| `coverage` | — | **7.17.2** | 7.17.2 | Nuevo | Añadido (T007-12) |
| `pip-audit` | — | **2.10.1** | 2.10.1 | Nuevo | Añadido |
| `pylint` | 4.0.9 | **4.1.3** | 4.1.3 | Menor | Aplicado |
| `isort` | 5.13.2 | 5.13.2 | 9.0.2 | Mayor | Pendiente de aprobación |
| `pylint-django` | 2.8.0 | 2.8.0 | 2.8.0 | — | Sin cambio |

### 2.3 Eliminado por falta de uso

`requests` y sus transitivas `certifi`, `charset-normalizer`, `idna` y `urllib3` no se
importan en el proyecto. Se eliminaron del archivo de producción.

Evidencia:

```bash
python specs/tools/check_dependencies.py --strict
# == Uso en el código ==
# Sin uso: ninguna
```

### 2.4 Frontend

| Recurso | Antes | Después |
| --- | --- | --- |
| Tailwind CSS (CDN) | Sin versión | `https://cdn.tailwindcss.com/3.4.19` |
| JetBrains Mono (Google Fonts) | Gestionada por Google | Sin cambio |

La última 3.x es 3.4.19; la 4.3.5 requiere una migración de configuración y queda como
tarea separada (`T006`/`T007`, build local).

### 2.5 Runtime y CI

| Recurso | Antes | Después |
| --- | --- | --- |
| Python | `3.12.1` en Render, `3.12` en CI | `.python-version` = 3.12.1; CI lo lee del archivo |
| Instalación de CI | `requirements.txt` | `requirements-dev.txt` |

## 3. Seguridad

```bash
pip-audit -r requirements.txt      # No known vulnerabilities found
pip-audit -r requirements-dev.txt  # No known vulnerabilities found
```

Sin avisos abiertos en la fecha del informe.

## 4. Verificación

| Comprobación | Comando | Resultado |
| --- | --- | --- |
| Settings | `manage.py check` | 0 issues |
| Migraciones | `manage.py makemigrations --check --dry-run` | No changes detected |
| Pruebas | `manage.py test` | 26 tests OK |
| Pruebas en entorno limpio | venv temporal solo con `requirements.txt` | 26 tests OK |
| Imports | `isort --check-only .` | 0 |
| Lint (informativo) | `pylint backend` | 5,29/10 (incluye migraciones) |
| Estáticos | `manage.py collectstatic --noinput` | 130 post-procesados |
| Coherencia | `pip check` | No broken requirements found |
| Inventario | `specs/tools/check_dependencies.py --strict` | OK |
| Acciones | `act`/CI | Pendiente de la primera ejecución en GitHub |

Transitivas resueltas en el entorno limpio: `asgiref 3.13.0`, `packaging 26.3`,
`sqlparse 0.6.1`, `psycopg-binary 3.3.8`, `typing_extensions 4.16.0`, `tzdata 2026.6`.

## 5. Reversiones

Ninguna. Todos los grupos aplicados pasaron la verificación.

## 6. Pendientes y riesgos

| Pendiente | Motivo | Tarea |
| --- | --- | --- |
| Django 6.1.3 | Salto mayor; 5.2 es LTS y sigue soportada | Tarea nueva al aprobar |
| gunicorn 27.0.0 | Salto mayor; requiere prueba de despliegue | Tarea nueva al aprobar |
| isort 9.0.2 | Mayor; puede cambiar el formato de imports | Tarea nueva al aprobar |
| Tailwind 4.3.5 | Requiere cambio de configuración o build local | `T006`/`T007` |
| Lockfile de transitivas | Hoy se resuelven libres dentro de los rangos | Backlog `010` |

Riesgo principal: al fijar solo dependencias directas, las transitivas pueden cambiar
entre instalaciones. La mitigación prevista es `pip-compile` con hashes (backlog).
