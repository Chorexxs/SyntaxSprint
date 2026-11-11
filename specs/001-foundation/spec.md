# Spec 001 — Fundación del proyecto

| Campo | Valor |
| --- | --- |
| Estado | Implementada (backlog en `tasks.md`) |
| Versión | 1.0 |
| Depende de | 000-overview |
| Archivos principales | `syntax_sprint/settings.py`, `syntax_sprint/urls.py`, `backend/apps.py`, `backend/admin.py`, `requirements.txt` |

## 1. Contexto y problema

Todo el producto depende de una configuración correcta de Django: rutas raíz, app
`backend`, resolución de plantillas, estáticos, base de datos y lectura de secretos
desde el entorno. Hoy funciona, pero contiene restos de una estructura anterior, imports
sin usar y el modelo principal no está disponible en el admin.

## 2. Objetivos

1. Mantener una configuración reproducible mediante `.env`.
2. Resolver plantillas y estáticos desde una única ubicación documentada.
3. Exponer `TypingTestResult` en Django Admin.
4. Alinear las dependencias con la versión real de Django.

### No objetivos

- Migrar a PostgreSQL.
- Introducir Docker o CI (ver 007).
- Reorganizar la app en varias apps Django.

## 3. Requisitos funcionales

| ID | Requisito | Prioridad |
| --- | --- | --- |
| RF-001-01 | Al arrancar, el sistema debe leer `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` desde `.env`. | Alta |
| RF-001-02 | El sistema debe registrar la app `backend` en `INSTALLED_APPS`. | Alta |
| RF-001-03 | El sistema debe resolver plantillas desde `BASE_DIR/templates`. | Alta |
| RF-001-04 | El sistema debe servir estáticos desde `BASE_DIR/static` en desarrollo. | Alta |
| RF-001-05 | El sistema debe exponer Django Admin en `/admin/`. | Media |
| RF-001-06 | El administrador debe poder listar, buscar y filtrar `TypingTestResult`. | Media |
| RF-001-07 | El sistema debe usar SQLite en `BASE_DIR/db.sqlite3`. | Alta |
| RF-001-08 | El proyecto debe declarar dependencias reproducibles en `requirements.txt`. | Alta |
| RF-001-09 | La documentación debe indicar la estructura real de directorios. | Media |

## 4. Reglas de negocio y validaciones

| Regla | Comportamiento |
| --- | --- |
| `SECRET_KEY` ausente | El arranque debe fallar con un error claro, no usar un valor por defecto. |
| `ALLOWED_HOSTS` vacío | Debe interpretarse como lista vacía, no como `['']`. |
| `DEBUG` distinto de booleano | Debe fallar o coercionar explícitamente. |
| Plantillas fuera de `BASE_DIR/templates` | No deben resolverse (eliminar ruta heredada). |

## 5. Contratos

### Configuración

| Variable | Tipo | Ejemplo | Obligatoria |
| --- | --- | --- | --- |
| `SECRET_KEY` | str | `django-insecure-...` | Sí |
| `DEBUG` | bool | `True` | Sí |
| `ALLOWED_HOSTS` | CSV | `127.0.0.1,localhost` | Sí |

### Rutas raíz

| Ruta | Destino |
| --- | --- |
| `/admin/` | `admin.site.urls` |
| `/` y resto | `backend.urls` |

## 6. Requisitos no funcionales

| ID | Requisito |
| --- | --- |
| RNF-001-01 | `python manage.py check` debe terminar sin errores. |
| RNF-001-02 | `pylint` no debe reportar imports duplicados ni sin usar en `backend/views.py`. |
| RNF-001-03 | `.env` nunca debe versionarse; debe existir `.env.example`. |

## 7. Criterios de aceptación

- **CA-001-01** Dado un `.env` válido, cuando ejecuto `runserver`, entonces el servidor arranca sin warnings de configuración.
- **CA-001-02** Dado el admin autenticado como superusuario, cuando abro `/admin/`, entonces veo `TypingTestResult` y puedo filtrar por usuario y fecha.
- **CA-001-03** Dado que borro `templates/` de la raíz del repo, cuando renderizo `/`, entonces la portada sigue funcionando.
- **CA-001-04** Dado `requirements.txt`, cuando creo un entorno limpio, entonces `pip install -r requirements.txt` instala la versión de Django documentada.

## 8. Fuera de alcance

- Configuración multi-entorno (staging/producción separados).
- Gestión de secretos en la nube.
- Migración de base de datos.

## 9. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
| --- | --- | --- |
| `requirements.txt` declara Django 5.2.6 y README 5.0.7 | Entornos inconsistentes | T001-05 |
| Ruta de plantillas heredada `BASE_DIR.parent/templates` | Confusión y 404 silenciosos | T001-04 |
| `settings.py` sin configuración de producción | Riesgo en despliegue | 007 |
| Sin `.env.example` | Onboarding difícil | T001-06 |

## 10. Referencias de código

- `syntax_sprint/syntax_sprint/settings.py`
- `syntax_sprint/syntax_sprint/urls.py`
- `syntax_sprint/backend/apps.py`
- `syntax_sprint/backend/admin.py`
- `requirements.txt`
