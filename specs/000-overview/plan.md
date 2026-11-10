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
├── backend/urls.py         → 6 rutas de aplicación
├── backend/views.py        → vistas función + catálogo de snippets
├── backend/models.py       → TypingTestResult
└── db.sqlite3              → persistencia
```

## 3. Flujo principal

```text
1. GET /                      → index.html (público)
2. POST /get_python_function  → snippet aleatorio {name, code}
3. Usuario escribe 30 s       → WPM/accuracy en cliente
4. POST /save_typing_test_result (auth + CSRF) → crear TypingTestResult
5. GET /profile (auth)        → historial + promedios
```

## 4. Estructura de directorios real

```text
SyntaxSprint/
├── AGENTS.md
├── README.md
├── requirements.txt
├── specs/
└── syntax_sprint/              # BASE_DIR
    ├── manage.py
    ├── db.sqlite3
    ├── backend/
    │   ├── models.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── admin.py
    │   ├── tests.py
    │   └── migrations/0001_initial.py
    ├── syntax_sprint/
    │   ├── settings.py
    │   └── urls.py
    ├── templates/
    │   ├── index.html
    │   ├── login.html
    │   ├── signup.html
    │   └── profile.html
    └── static/
        ├── css/styles.css
        ├── js/script.js
        └── icon/icon.svg
```

> Desviación conocida: `README.md` describe `templates/` y `static/` en la raíz del
> repositorio, pero viven dentro de `syntax_sprint/`. Ver tarea `T007-08`.

## 5. Decisiones de arquitectura (ADR resumidos)

| ID | Decisión | Motivo | Consecuencia |
| --- | --- | --- | --- |
| ADR-01 | Vistas función en lugar de CBV | Simplicidad y tamaño del proyecto | Repetición de `login_required` |
| ADR-02 | Catálogo de snippets en memoria (`views.py`) | Evitar BD para contenido estático | Archivo grande; difícil de mantener |
| ADR-03 | Cálculo de WPM en cliente | Feedback en tiempo real | Resultado manipulable; validar en servidor |
| ADR-04 | SQLite | Simplicidad y despliegue barato | Límites de concurrencia |
| ADR-05 | Tailwind por CDN | Sin paso de build | Dependencia de red y warning de producción |
| ADR-06 | Sesiones de Django | Stack nativo | Sin API tokens |

## 6. Deuda técnica transversal

| Deuda | Ubicación | Feature que la resuelve |
| --- | --- | --- |
| Suite de pruebas vacía | `backend/tests.py` | 007 |
| Modelo no registrado en admin | `backend/admin.py` | 001 |
| Imports duplicados y sin usar | `backend/views.py` | 001 |
| Sin validación de rango de WPM/accuracy | `backend/views.py` | 005 |
| CSRF no inicializado en portada | `templates/index.html` | 004 |
| Sin settings de seguridad de producción | `settings.py` | 007 |
| README desactualizado | `README.md` | 007 |
| Código de tema duplicado en 4 plantillas | `templates/*.html` | 006 |

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
