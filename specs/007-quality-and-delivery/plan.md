# Plan técnico 007 — Calidad, seguridad y despliegue

| Campo | Valor |
| --- | --- |
| Spec | `specs/007-quality-and-delivery/spec.md` |
| Estado | Aprobado |
| Última revisión | 2026-11-10 |

## 1. Enfoque

Primero construir la red de seguridad (tests del comportamiento actual), después
endurecer la configuración y finalmente automatizar. No se refactoriza lógica de negocio
antes de tener pruebas que la protejan.

## 2. Cambios por archivo

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `backend/tests.py` | Reescribir | Tests por clase: `AuthTests`, `SnippetTests`, `ResultTests`, `ProfileTests`. |
| `syntax_sprint/syntax_sprint/settings.py` | Modificar | Bloque `if not DEBUG` con seguridad HTTPS y estáticos. |
| `requirements.txt` | Modificar | Añadir `coverage`, `pytest-django` (opcional), fijar versiones. |
| `.github/workflows/ci.yml` | Crear | Job de lint, check, migraciones y tests. |
| `README.md` | Modificar | Estructura real, variables, despliegue. |
| `specs/traceability.md` | Modificar | Estado final. |

## 3. Configuración de producción propuesta

```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"
```

Estáticos: añadir `whitenoise` como middleware o documentar el servidor web que sirve
`staticfiles/`.

## 4. Estructura de tests

```python
class AuthTests(TestCase):
    def test_signup_creates_user_and_logs_in(self): ...
    def test_signup_duplicate_email(self): ...
    def test_signup_password_mismatch(self): ...
    def test_login_valid(self): ...
    def test_login_invalid(self): ...
    def test_logout_requires_auth(self): ...

class SnippetTests(TestCase):
    def test_post_valid_language(self): ...
    def test_unknown_language_falls_back_to_python(self): ...
    def test_get_defaults_to_python(self): ...
    def test_invalid_json_returns_400(self): ...

class ResultTests(TestCase):
    def test_save_requires_login(self): ...
    def test_save_valid(self): ...
    def test_save_invalid_payload(self): ...
    def test_save_get_not_allowed(self): ...
    def test_save_rejects_out_of_range(self): ...

class ProfileTests(TestCase):
    def test_profile_requires_login(self): ...
    def test_profile_only_own_results(self): ...
    def test_profile_averages(self): ...
    def test_profile_empty_state(self): ...
```

## 5. Pipeline CI

```yaml
name: ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: python syntax_sprint/manage.py check
      - run: python syntax_sprint/manage.py makemigrations --check --dry-run
      - run: python syntax_sprint/manage.py test backend
      - run: isort --check-only syntax_sprint/
      - run: pylint syntax_sprint/
```

Variables de entorno en CI: `SECRET_KEY=test`, `DEBUG=False`, `ALLOWED_HOSTS=localhost,testserver`.

## 6. Alternativas consideradas

| Alternativa | Pros | Contras | ¿Elegida? |
| --- | --- | --- | --- |
| `pytest` + `pytest-django` | Mejor DX, fixtures | Dependencia nueva | Opcional |
| `django.test.TestCase` | Nativo, cero deps | Menos flexible | Sí |
| GitHub Actions | Gratis para el repo | Requiere repo en GitHub | Sí |
| Pre-commit hooks | Feedback local | Configuración extra | Backlog |

## 7. Estrategia de pruebas

| Nivel | Qué se prueba | Herramienta |
| --- | --- | --- |
| Unitario | Cálculos y modelo | `TestCase` |
| Integración | Vistas y JSON | `Client` |
| Estático | Imports y estilo | `isort`, `pylint` |
| CI | Todo lo anterior | GitHub Actions |

## 8. Riesgos y mitigación

| Riesgo | Probabilidad | Mitigación |
| --- | --- | --- |
| Tests fallan por CSRF | Media | Usar `Client()` normal; CSRF desactivado en tests por defecto |
| CI sin `ALLOWED_HOSTS` | Media | Definir `testserver` en el workflow |
| `pylint` con muchos avisos heredados | Alta | Fijar umbral y reducir deuda gradualmente |
| Bloqueo por HSTS | Baja | Empezar con 1 hora |

## 9. Orden de implementación

1. Tests del comportamiento actual (auth, snippets, resultados, perfil).
2. Correcciones que descubran los tests.
3. Configuración de producción.
4. Workflow de CI.
5. Documentación y trazabilidad.

## 10. Notas de despliegue

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn syntax_sprint.wsgi:application --bind 0.0.0.0:8000
```

Checklist previo:

- [ ] `.env` con `DEBUG=False` y `ALLOWED_HOSTS` reales.
- [ ] Migraciones aplicadas.
- [ ] `collectstatic` ejecutado.
- [ ] HTTPS y cookies seguras verificadas.
- [ ] Backup de la base de datos.

## 11. Render y estáticos

La app se despliega en Render (`syntaxsprint.onrender.com`). Cambios de esta fase:

| Cambio | Motivo |
| --- | --- |
| `WhiteNoiseMiddleware` + `STORAGES` | Servir CSS/JS con `DEBUG=False` |
| `collectstatic` en el build | Generar `staticfiles/` y el manifest |
| `RENDER_EXTERNAL_HOSTNAME` | Añadir automáticamente host y CSRF de Render |
| `DB_PATH` | Permitir SQLite en un disco persistente |
| `DATABASE_URL` + `dj-database-url` | Usar PostgreSQL gestionado y evitar SQLite efímero |
| `render.yaml` | Blueprint reproducible con build/start/variables |
| `DEPLOY.md` | Runbook de rotación, backup, migración y rollback |

Comandos:

```bash
pip install -r requirements.txt
python syntax_sprint/manage.py collectstatic --noinput
python syntax_sprint/manage.py migrate --noinput
gunicorn --chdir syntax_sprint syntax_sprint.wsgi:application
```

Riesgo principal: Render free no ofrece disco persistente. Sin PostgreSQL ni disco,
el SQLite se pierde en cada redeploy. La opción recomendada es `DATABASE_URL` con
Render Postgres; la alternativa es un disco de pago con `DB_PATH=/var/data/db.sqlite3`.

Antes de mergear a `main`, hacer backup (`dumpdata`) porque Render redepliega
automáticamente al detectar el push.
