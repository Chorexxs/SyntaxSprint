# Plan técnico 010 — Dependencias y actualización bajo demanda

| Campo | Valor |
| --- | --- |
| Spec | `specs/010-dependencies/spec.md` |
| Estado | Aprobado |
| Autor | — |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Convertir la actualización de dependencias en un **procedimiento de seis pasos** que se
ejecuta solo cuando el responsable lo pide: inventariar, auditar, clasificar, aplicar
parches/menores, verificar y documentar. Las actualizaciones mayores quedan aisladas en
ramas y tareas propias. No se introduce ninguna herramienta nueva de ejecución: `pip`,
`pip-audit` y los comandos ya usados por CI son suficientes.

La automatización continua (Dependabot) se trata como complemento, no como sustituto:
detecta y abre PRs, pero el procedimiento manual decide los saltos grandes, el runtime
de Python y los CDN.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `specs/010-dependencies/spec.md` | Añadir | Requisitos, reglas y criterios. |
| `specs/010-dependencies/plan.md` | Añadir | Este documento con el inventario. |
| `specs/010-dependencies/tasks.md` | Añadir | Tareas del procedimiento. |
| `requirements.txt` | Modificar | Quitar `requests` y transitivas; separar dev. |
| `requirements-dev.txt` | Añadir | `pylint`, `pylint-django`, `isort`, `coverage`, `pip-audit`. |
| `audits/dependencies/` | Añadir | Un informe por ejecución. |
| `specs/tools/check_dependencies.py` | Añadir | Inventario sin dependencias externas. |
| `syntax_sprint/templates/*.html` | Modificar | Fijar la versión del CDN de Tailwind. |
| `render.yaml` | Modificar | Fuente única de la versión de Python. |

## 3. Inventario actual (2026-11-10)

### 3.1 Dependencias de Python

| Paquete | Versión | Tipo | Uso |
| --- | --- | --- | --- |
| `Django` | 5.2.19 | Prod | Framework (serie LTS 5.2) |
| `dj-database-url` | 3.1.2 | Prod | `DATABASE_URL` |
| `gunicorn` | 25.3.0 | Prod | Servidor WSGI |
| `psycopg[binary]` | 3.3.8 | Prod | Driver PostgreSQL |
| `python-decouple` | 3.8 | Prod | `.env` |
| `whitenoise` | 6.12.0 | Prod | Estáticos |
| `coverage` | 7.17.2 | Dev | Cobertura |
| `isort` | 5.13.2 | Dev | Orden de imports |
| `pip-audit` | 2.10.1 | Dev | Vulnerabilidades |
| `pylint` | 4.1.3 | Dev | Lint |
| `pylint-django` | 2.8.0 | Dev | Plugin de pylint |

Las transitivas (`asgiref`, `sqlparse`, `tzdata`, `packaging`, `platformdirs`, etc.) no se
fijan: las resuelve pip dentro de los rangos de las dependencias directas. El lockfile
queda en el backlog.

> Eliminados en esta ejecución: `requests==2.33.1` y sus transitivas `certifi`,
> `charset-normalizer`, `idna` y `urllib3`, sin uso en el código (`T010-06`).

### 3.2 Dependencias de frontend

| Recurso | Origen | Versión |
| --- | --- | --- |
| Tailwind CSS | `https://cdn.tailwindcss.com/3.4.17` | 3.4.17 (fijada) |
| JetBrains Mono | Google Fonts | Gestionada por Google |
| JavaScript | Propio (`static/js`) | — |

No hay `package.json` ni `node_modules`: no existe ecosistema npm que actualizar.

### 3.3 Runtime, CI e infraestructura

| Recurso | Versión | Fuente |
| --- | --- | --- |
| Python | 3.12.1 | `.python-version` (CI lo lee) |
| Render | 3.12.1 | `render.yaml`, validado por el verificador |
| `actions/checkout` | v4 | `.github/workflows/ci.yml` |
| `actions/setup-python` | v5 | `.github/workflows/ci.yml` |
| PostgreSQL | InsForge | `DATABASE_URL` |
| InsForge CLI | `>= 0.2.8` | `npx @insforge/cli` (documentado) |

## 4. Procedimiento

```text
1. Comprobar árbol limpio y main sincronizado (RF-010-11)
2. Inventariar y comparar versiones (RF-010-02, RF-010-03)
3. pip-audit (RF-010-04)
4. Clasificar parche / menor / mayor / seguridad (RF-010-05)
5. Rama para parches+menores; mayores aparte (RF-010-06, RF-010-07)
6. Verificar y documentar (RF-010-08, RF-010-09, RF-010-10)
```

## 5. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| Solo Dependabot/Renovate | Continuo, PRs automáticos | No decide mayores ni CDN; ruido si no se atiende | Complemento (`T010-09`) |
| Procedimiento manual documentado | Control, evidencia, sin dependencias | Requiere disciplina | **Sí** |
| `pip-tools` (`requirements.in` → lock) | Resolución reproducible | Nueva herramienta y flujo | No (spec aparte) |
| Poetry / uv | Lockfile y entorno | Reescritura del flujo actual | No |
| `pip install --upgrade` masivo | Rápido | Sin control ni trazabilidad | **No** |

## 6. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Unitario/integración | Que la actualización no rompe el backend | `manage.py test` (26 casos) |
| Configuración | Settings válidos y migraciones al día | `check`, `makemigrations --check` |
| Estilo | Imports ordenados | `isort --check-only` |
| Estáticos | `collectstatic` sigue funcionando | `manage.py collectstatic --noinput` |
| Manual | El test de typing sigue funcionando en navegador | Checklist de `004` |

## 7. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Un parche rompe una vista no cubierta | Media | Checklist manual del test de typing |
| Eliminar `requests` rompe algo oculto | Baja | Búsqueda previa + suite + `check` |
| Salto mayor de Django | Media | Rama y tarea propias |
| Tailwind CDN cambia de versión mayor | Media | Fijar versión (`T010-07`) |
| CI y `render.yaml` divergen en Python | Baja | Fuente única (`T010-06`) |

## 8. Orden de implementación

1. Crear la estructura del spec y el inventario (`T010-01`, `T010-02`).
2. Añadir el verificador de inventario y la plantilla de informe (`T010-03`).
3. Separar dependencias de desarrollo (`T010-05`).
4. Eliminar dependencias sin uso (`T010-04`).
5. Fijar el CDN de Tailwind (`T010-07`).
6. Activar Dependabot (`T010-09`).
7. Primera ejecución real del procedimiento (`T010-09`).

## 9. Notas de despliegue

- El procedimiento **no** despliega: el hosting se decidirá aparte (Vercel probablemente).
- No se tocan variables de entorno ni secretos.
- `render.yaml` sigue siendo la referencia actual hasta que se elija el hosting definitivo.
- Tras actualizar, el redeploy del hosting debe verificarse con `check --deploy`.
