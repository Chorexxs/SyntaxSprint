# Actualización de dependencias — 2026-11-23

| Campo | Valor |
| --- | --- |
| Fecha | 2026-11-23 |
| Commit de partida | `f20b459` |
| Alcance | Parches de Python (producción y desarrollo) |
| Procedimiento | `specs/010-dependencies/spec.md` |
| Resultado | Sin vulnerabilidades; 3 parches aplicados; `coverage` 7.17.4 queda para la próxima ejecución |

## 1. Motivo

Dependabot agrupó los parches semanales de `pip` (`.github/dependabot.yml`) en el PR #7.
El responsable pidió aplicarlos siguiendo el procedimiento de la spec `010`.

## 2. Inventario y acciones

### 2.1 Producción

| Paquete | Antes | Después | Última | Tipo | Acción |
| --- | --- | --- | --- | --- | --- |
| `psycopg[binary]` | 3.3.8 | **3.3.9** | 3.3.9 | Parche | Aplicado |
| `Django` | 5.2.19 | 5.2.19 | 6.1.3 | Mayor | Pendiente de aprobación |
| `gunicorn` | 25.3.0 | 25.3.0 | 27.0.1 | Mayor | Pendiente de aprobación |
| `dj-database-url` | 3.1.2 | 3.1.2 | 3.1.2 | — | Sin cambio |
| `python-decouple` | 3.8 | 3.8 | 3.8 | — | Sin cambio |
| `whitenoise` | 6.12.0 | 6.12.0 | 6.12.0 | — | Sin cambio |

### 2.2 Desarrollo

| Paquete | Antes | Después | Última | Tipo | Acción |
| --- | --- | --- | --- | --- | --- |
| `coverage` | 7.17.2 | **7.17.3** | 7.17.4 | Parche | Aplicado; la 7.17.4 se publicó después del PR |
| `pylint` | 4.1.3 | **4.1.4** | 4.1.4 | Parche | Aplicado |
| `isort` | 5.13.2 | 5.13.2 | 9.0.2 | Mayor | Pendiente de aprobación |
| `pip-audit` | 2.10.1 | 2.10.1 | 2.10.1 | — | Sin cambio |
| `pylint-django` | 2.8.0 | 2.8.0 | 2.8.0 | — | Sin cambio |

No se modificaron versiones del frontend (`tailwindcss`, `vitest`, `jsdom`) ni del
runtime (Python 3.12).

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
| Pruebas | `manage.py test` | 88 encontradas: 87 OK + 1 omitida (POSIX en Windows) |
| Imports | `isort --check-only .` | 0 |
| Lint | `pylint backend` | 10.00/10 |
| Estáticos | `manage.py collectstatic --noinput` | 5 copiados, 133 post-procesados |
| Inventario | `specs/tools/check_dependencies.py --strict` | OK |
| CI del PR | workflow `CI` (run 45119298166) | En verde |
| Preview | Vercel | En verde |

Entorno usado: `venv` del repositorio (Python 3.12.1) con `requirements-dev.txt`.
El PR se mergeó como `729bb5c`.

## 5. Reversiones

Ninguna. El grupo aplicado pasó la verificación completa.

## 6. Pendientes y riesgos

| Pendiente | Motivo | Acción |
| --- | --- | --- |
| `coverage` 7.17.4 | Publicada después del PR; es un parche menor | Se aplicará en la próxima revisión semanal |
| Django 6.1.3 | Salto mayor; 5.2 sigue siendo LTS | Requiere plan y ventana de pruebas |
| gunicorn 27.0.1 | Salto mayor; afecta al arranque en Render | Requiere prueba de despliegue |
| isort 9.0.2 | Mayor; puede cambiar el formato de imports | Requiere rama propia |
| Vitest 5 | Exige Node ≥ 22.12 y el CI usa Node 20 | Backlog `010` |

Riesgo principal sin cambios: las dependencias transitivas se resuelven libres porque
solo se fijan las directas. La mitigación sigue siendo `requirements.in` +
`pip-compile` con hashes (backlog de la spec `010`).
