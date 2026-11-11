# Plan técnico 000 — Arquitectura global

| Campo | Valor |
| --- | --- |
| Spec | `specs/000-overview/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Aplicación **Django MVT** monolítica. El backend expone cuatro páginas HTML renderizadas
con el motor de plantillas y dos endpoints JSON (`get_python_function`,
`save_typing_test_result`). No hay API REST ni framework frontend: una única clase
JavaScript (`TypingTest`) encapsula el estado del test y se comunica con el backend por
`fetch`. La persistencia es SQLite con el ORM de Django.

## 2. Mapa de capas

```text
Navegador
├── templates/*.html        → HTML + Tailwind CDN + tokens CSS
├── static/js/script.js     → motor de test (TypingTest)
└── static/css/styles.css   → variables de tema y estados
        │  fetch (JSON)
        ▼
Django (syntax_sprint/)
├── syntax_sprint/urls.py   → admin/ + backend.urls
├── backend/urls.py         → 8 rutas de aplicación
├── backend/views.py        → portada pública
├── backend/snippet_views.py → endpoint de fragmentos
├── backend/auth_views.py   → registro, login y logout
├── backend/result_views.py → guardado de resultados y perfil
├── backend/validators.py   → validación de JSON y rangos
├── backend/snippets.py     → catálogo de fragmentos
├── backend/models.py       → TypingTestResult, SnippetRequest
├── backend/analytics.py    → registro y métricas de producto (spec 011)
└── db.sqlite3              → persistencia local (producción: PostgreSQL)
```

## 3. Flujo principal

```text
1. GET /                      → index.html (público)
2. POST /get_python_function  → snippet aleatorio {name, code} + evento de analítica
3. Usuario escribe 30 s       → WPM/accuracy en cliente
4. POST /save_typing_test_result (auth + CSRF) → crear TypingTestResult
5. GET /profile (auth)        → historial + promedios
6. manage.py analytics_report → métricas de la spec 000 §7
```

## 4. Estructura de directorios real

```text
SyntaxSprint/
├── AGENTS.md
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .python-version
├── specs/
└── syntax_sprint/              # BASE_DIR
    ├── manage.py
    ├── db.sqlite3
    ├── backend/
    │   ├── models.py
    │   ├── views.py
    │   ├── snippet_views.py
    │   ├── auth_views.py
    │   ├── result_views.py
    │   ├── validators.py
    │   ├── snippets.py
    │   ├── analytics.py
    │   ├── management/commands/analytics_report.py, purge_analytics.py
    │   ├── urls.py
    │   ├── admin.py
    │   ├── tests.py
    │   └── migrations/0001_initial.py, 0002_snippetrequest.py
    ├── syntax_sprint/
    │   ├── settings.py
    │   └── urls.py
    ├── templates/
    │   ├── base.html
    │   ├── index.html
    │   ├── login.html
    │   ├── signup.html
    │   └── profile.html
    └── static/
        ├── css/styles.css
        ├── js/script.js
        └── icon/icon.svg
```

> Desviación resuelta: `README.md` ya describe la estructura real (ver `T007-14`).

## 5. Decisiones de arquitectura (ADR resumidos)

| ID | Decisión | Motivo | Consecuencia |
| --- | --- | --- | --- |
| ADR-01 | Vistas función en lugar de CBV | Simplicidad y tamaño del proyecto | Repetición de `login_required` |
| ADR-02 | Catálogo de snippets en memoria (`backend/snippets.py`) | Evitar BD para contenido estático | Un módulo de datos grande; se mantiene aparte de las vistas |
| ADR-03 | Cálculo de WPM en cliente | Feedback en tiempo real | Resultado manipulable; validar en servidor |
| ADR-04 | SQLite en local; PostgreSQL (InsForge) en producción | Simplicidad en desarrollo y persistencia real | Dos motores que deben comportarse igual; lo cubren los tests |
| ADR-05 | Tailwind por CDN (sustituido por build local el 2026-11-11) | Sin paso de build | Dependencia de red; versión fijada en 3.4.17 |
| ADR-06 | Sesiones de Django | Stack nativo | Sin API tokens |
| ADR-07 | Analítica propia en PostgreSQL | Sin cookies de terceros ni dependencias nuevas | Hay que mantener el modelo, la purga y los comandos |

## 6. Deuda técnica transversal

| Deuda | Ubicación | Feature que la resuelve |
| --- | --- | --- |
| Foco no visible y controles sin nombre accesible | `templates/*.html`, `static/css/styles.css` | 006 |
| Historial del perfil sin paginación | `backend/result_views.py` | 005 |
| Faltan tests de perfil, promedios y cascada | `backend/tests.py` | 005/007 |
| Líneas > 100 en el catálogo y en `script.js` | `backend/snippets.py`, `static/js/script.js` | 008 |
| Contadores al pegar y reinicio del intervalo | `static/js/script.js` | 004 |
| Mensajes de registro divergentes de la spec | `backend/auth_views.py` | 002 |
| Ruta heredada en `TEMPLATES` | `settings.py` | 001 |
| PII y secretos en el historial | `db.sqlite3`, historial de Git | 009 |

## 7. Estrategia de pruebas global

| Nivel | Alcance | Herramienta |
| --- | --- | --- |
| Unitario | Modelos, cálculos | `django.test.TestCase` |
| Integración | Vistas, auth, JSON, CSRF | `django.test.Client` |
| Manual | Motor de typing, temas, responsive | Checklist en `tasks.md` |
| Estático | Estilo e imports | `pylint`, `isort` |

## 8. Orden de implementación recomendado

1. `001-foundation` (limpieza y base).
2. `007-quality-and-delivery` fase 1 (tests que protegen el comportamiento actual).
3. `002-authentication` (endurecimiento).
4. `004-typing-engine` y `005-results-and-profile` (correcciones funcionales).
5. `006-ui-and-theming` (accesibilidad y deduplicación).
6. `007` fases restantes (CI y despliegue).

## 9. Notas de despliegue

- Servidor de aplicación: Gunicorn con `syntax_sprint.wsgi`.
- Estáticos: `collectstatic` hacia `staticfiles/`; requiere servidor web o CDN.
- Variables: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`.
- Base de datos: SQLite local; migrar a PostgreSQL si hay concurrencia real.
