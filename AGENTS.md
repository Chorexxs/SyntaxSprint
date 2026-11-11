# AGENTS.md — Guía de desarrollo de SyntaxSprint

SyntaxSprint es una aplicación web **Django 5.x** para practicar velocidad de escritura
con fragmentos de código reales. Mide WPM y precisión en tests de 30 segundos, guarda el
historial del usuario y calcula promedios.

> Este repositorio usa **Spec-Driven Development (SDD)**. La fuente de verdad está en
> `specs/`. Antes de escribir código, lee `specs/README.md`, `specs/constitution.md` y la
> carpeta de la funcionalidad que vas a tocar.

---

## 1. Snapshot del proyecto

| Aspecto | Valor |
| --- | --- |
| Framework | Django 5.x (MVT) |
| Base de datos | InsForge PostgreSQL (`DATABASE_URL`) |
| Frontend | Plantillas Django + Tailwind compilado + CSS propio |
| JavaScript | Vanilla ES6+ (clase `TypingTest`); jQuery 3.x permitido |
| Servidor | Gunicorn (`syntax_sprint.wsgi`) |
| Configuración | `python-decouple` + `.env` |
| Pruebas | `django.test.TestCase` (33 tests, suite en verde) |
| Lint | `pylint`, `isort` |
| App principal | `backend` |

## 2. Estructura real

```text
SyntaxSprint/
├── AGENTS.md
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── .python-version
├── specs/                       # Spec-Driven Development
│   ├── README.md
│   ├── constitution.md
│   ├── traceability.md
│   ├── templates/
│   └── 000-overview/ … 007-quality-and-delivery/
└── syntax_sprint/               # BASE_DIR
    ├── manage.py
    ├── db.sqlite3
    ├── backend/                 # app: models, vistas por dominio, urls, admin, tests
    ├── syntax_sprint/           # settings, urls, wsgi/asgi
    ├── templates/               # base, index, login, signup, profile
    └── static/                  # css/styles.css, js/script.js, icon/
```

> El `README.md` describe una estructura más plana; la real es la de arriba. Ver
> `specs/001-foundation` y `specs/007-quality-and-delivery`.

## 3. Comandos

```bash
# Todas las rutas son relativas a la raíz del repositorio
cd syntax_sprint

# Servidor de desarrollo
python manage.py runserver

# Dependencias de desarrollo (incluye producción)
pip install -r ../requirements-dev.txt

# Tailwind local (solo si cambias clases en plantillas o JS)
npm install
npm run build:css

# Verificación de dependencias (sin red)
python ../specs/tools/check_dependencies.py --strict

# Migraciones
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations --check --dry-run

# Pruebas
python manage.py test
python manage.py test backend.tests
python manage.py test backend.tests.AuthTests.test_login_valid

# Verificación
python manage.py check
python manage.py check --deploy

# Lint e imports (desde la raíz)
isort --check-only syntax_sprint/
isort syntax_sprint/

# Lint (desde syntax_sprint/)
cd syntax_sprint
pylint backend --rcfile=../.pylintrc

# Producción
python manage.py collectstatic --noinput
gunicorn syntax_sprint.wsgi:application --bind 0.0.0.0:8000
```

## 4. Mapa de rutas y contratos

| Método | Ruta | Vista | Auth | Respuesta |
| --- | --- | --- | --- | --- |
| GET | `/` | `index` | No | `index.html` |
| GET/POST | `/get_python_function` | `get_python_function` | No | `{name, code}` |
| GET/POST | `/signup` | `signup` | No | HTML / 302 |
| GET/POST | `/login` | `login` | No | HTML / 302 |
| GET | `/logout` | `logout` | Sí | 405 (solo POST) |
| POST | `/logout` | `logout` | Sí | 302 → `/` |
| GET | `/profile` | `profile` | Sí | `profile.html` |
| POST | `/save_typing_test_result` | `save_typing_test_result` | Sí | `{message}` |
| — | `/admin/` | Django Admin | Staff | HTML |

Modelo único: `TypingTestResult(user, wpm, accuracy, date)`.

## 5. Convenciones de código

### Imports (isort)

1. Biblioteca estándar
2. Paquetes de terceros
3. Django
4. Imports locales

### Nombres

- Funciones y variables: `snake_case` (`save_typing_test_result`)
- Clases: `PascalCase` (`TypingTest`, `TypingTestResult`)
- Constantes: `UPPER_SNAKE_CASE` (`CODE_SNIPPETS`)
- Modelos: `PascalCase` singular
- Nombres de URL: `snake_case`

### Tipos y formato

```python
def calculate_wpm(chars: int, time_seconds: float) -> float:
    return (chars / 5) / (time_seconds / 60)
```

- Máximo 100 caracteres por línea
- 4 espacios, sin tabs, sin espacios finales
- Anotaciones de tipo en funciones nuevas
- Español para documentación y mensajes; inglés para identificadores

### Django

- `@login_required(login_url="login")` en vistas protegidas
- `JsonResponse` para endpoints AJAX
- `messages` para feedback de usuario
- Códigos HTTP correctos: 200, 400, 405
- `on_delete=models.CASCADE` en FKs
- `__str__` en todos los modelos
- URLs con nombre y `redirect("nombre")`, nunca rutas hardcodeadas
- `{% csrf_token %}` en todo formulario y en páginas que hagan POST por `fetch`

### JavaScript

- `fetch` con `X-CSRFToken` para POST
- Manejar errores y respuestas no-2xx
- No introducir frameworks sin una spec aprobada
- Mantener los IDs del DOM usados por `TypingTest`

### Seguridad

- Nunca versionar secretos, `.env` ni claves
- Validar toda entrada en el servidor
- No exponer trazas internas al usuario
- `DEBUG=False` en producción

### Commits

- **Siempre en español.** Sin excepciones, ni siquiera en ramas personales.
- Asunto en imperativo y ≤ 72 caracteres: `Tipo: descripción`.
- Tipos permitidos, también en español: `Añadir`, `Corregir`, `Actualizar`,
  `Eliminar`, `Refactorizar`, `Documentar`, `Probar`, `Desplegar`.
- Cuerpo opcional en viñetas: qué cambia y por qué.
- Un commit por tarea (`T00X-NN`); no mezclar refactor, funcionalidad y formato.
- Referenciar la spec cuando aplique: `Refs: specs/00X-nombre`.

```text
Corregir validación de resultados del perfil

- Rechazar WPM negativo y accuracy fuera de 0–100
- Responder 400 ante JSON inválido
- Añadir pruebas de rangos

Refs: specs/005-results-and-profile
```

---

## 6. Flujo Spec-Driven Development

### 6.1 Regla de oro

**Ningún cambio de comportamiento sin requisito.** El orden es siempre:

```text
spec.md  →  plan.md  →  tasks.md  →  código  →  verificación  →  traceability.md
```

### 6.2 Dónde vive cada cosa

| Necesito… | Voy a… |
| --- | --- |
| Entender el producto | `specs/000-overview/spec.md` |
| Saber cómo está construido | `specs/000-overview/plan.md` |
| Ver qué falta | `specs/000-overview/tasks.md` |
| Trabajar en una funcionalidad | `specs/00X-*/spec.md` + `plan.md` + `tasks.md` |
| Crear una funcionalidad nueva | Copiar `specs/templates/*` a `specs/008-nombre/` |
| Verificar cobertura de requisitos | `specs/traceability.md` |
| Conocer las reglas no negociables | `specs/constitution.md` |

### 6.3 Anatomía de una spec

```markdown
# Spec 00X — Nombre
| Estado | Borrador / Aprobada / Implementada / Obsoleta |

## 1. Contexto y problema
## 2. Objetivos / No objetivos
## 3. Actores y casos de uso
## 4. Requisitos funcionales   → RF-00X-NN (formato EARS)
## 5. Reglas de negocio
## 6. Contratos (endpoints, modelos)
## 7. Requisitos no funcionales → RNF-00X-NN
## 8. Criterios de aceptación   → CA-00X-NN (Dado/Cuando/Entonces)
## 9. Fuera de alcance
## 10. Riesgos y deuda técnica
## 11. Referencias de código
```

Un requisito debe ser **verificable**. "Ser rápido" no es un requisito; "responder en
menos de 300 ms en local" sí lo es.

### 6.4 Anatomía de una tarea

```markdown
- [ ] **T00X-01** Verbo + resultado esperado.
  - Requisito: `RF-00X-01`
  - Archivos: `ruta/archivo.py`
  - DoD: cómo se comprueba que está hecha.
```

Estados: `[ ]` pendiente · `[x]` completada · `[!]` bloqueada.

### 6.5 Ciclo de trabajo

1. Leer la spec y las tareas pendientes de la funcionalidad.
2. Implementar **una tarea** por cambio, sin mezclar refactors.
3. Ejecutar su verificación (test, `check`, o checklist manual).
4. Marcar `[x]` y actualizar `traceability.md`.
5. Si el alcance cambia: actualizar `spec.md` **antes** de tocar código.
6. Registrar decisiones y deuda en `plan.md`, no en comentarios sueltos.

### 6.6 Definition of Ready

- [ ] Spec aprobada y con criterios de aceptación.
- [ ] Plan con archivos afectados y contratos.
- [ ] Tareas ordenadas por dependencia.
- [ ] Riesgos de seguridad y migración identificados.

### 6.7 Definition of Done

- [ ] Tareas de la funcionalidad en `[x]`.
- [ ] `python manage.py check` sin errores.
- [ ] `python manage.py test` en verde.
- [ ] `isort --check-only` y `pylint` sin errores nuevos.
- [ ] `spec.md` y `plan.md` reflejan la implementación.
- [ ] `traceability.md` actualizado.
- [ ] Sin secretos ni `DEBUG=True` versionados.

---

## 7. Checklist para agentes de IA

Antes de editar:

- [ ] Leí `specs/000-overview/spec.md` y la spec de la funcionalidad.
- [ ] Identifiqué el `RF-*` y la tarea `T*` que voy a satisfacer.
- [ ] Revisé `specs/constitution.md`.
- [ ] Comprobé si el archivo ya tiene trabajo del usuario sin commitear (`git status`).

Al editar:

- [ ] Cambio mínimo y consistente con el estilo circundante.
- [ ] No elimino archivos ni lógica sin investigarlos antes.
- [ ] No añado dependencias sin requisito explícito.
- [ ] No edito migraciones ya aplicadas.

Al terminar:

- [ ] Ejecuté la verificación de la tarea.
- [ ] Actualicé `tasks.md` y `traceability.md`.
- [ ] Reporté cualquier divergencia entre código y spec.
- [ ] Dejé claro qué quedó pendiente.

## 8. Deuda técnica conocida (priorizada)

Estado verificado el 2026-11-11: `manage.py check` 0 issues, `manage.py test` 33 tests
OK, `isort --check-only` sin avisos, `pylint` 10.00/10 y `code_metrics.py --strict` sin
incumplimientos. La antigua deuda "suite de pruebas vacía" ya está cerrada.

No hay deuda priorizada abierta. Tailwind se compila localmente desde el 2026-11-11
(`npm run build:css`).

> No quedan hallazgos **CRÍTICOS** abiertos. Evidencia:
> `audits/security/2026-11-11-verificacion.md`.

## 9. Seguridad — reglas rápidas

1. `.env` nunca se commitea; usa `.env.example`.
2. Toda vista que escribe datos: autenticación + CSRF + validación.
3. Los resultados se asocian siempre a `request.user`, nunca a un ID del cliente.
4. Los mensajes de error no revelan si un usuario existe.
5. En producción: HTTPS, cookies `Secure`, HSTS y `DEBUG=False`.

## 10. Auditorías bajo demanda

Las auditorías se ejecutan **solo cuando el usuario lo pide**. No son automáticas.

| Disparador | Spec a ejecutar | Herramienta |
| --- | --- | --- |
| "audita el código", "revisa la arquitectura", "¿esto es espagueti?" | `specs/008-code-audit/spec.md` | `specs/tools/code_metrics.py` |
| "audita la seguridad", "revisa filtraciones", "¿hay API keys?" | `specs/009-cybersecurity/spec.md` | `specs/tools/scan_secrets.py` |
| "revisa las dependencias", "actualiza las dependencias" | `specs/010-dependencies/spec.md` | `pip-audit`, `pip list --outdated` |

Reglas obligatorias:

1. **Solo lectura** en auditorías (008/009): no se corrige código durante la auditoría;
   los arreglos van en tareas. La actualización de dependencias (010) es la excepción:
   modifica `requirements.txt` en rama y commit propios, nunca junto a una funcionalidad.
2. **Evidencia**: cada hallazgo requiere `archivo:línea` o comando reproducible.
3. **Nunca imprimir secretos**: ni en consola, ni en el chat, ni en el informe. Usar
   `<redacted>`.
4. **Informe en español** en `audits/code/` o `audits/security/`.
5. **Trazabilidad**: cada hallazgo se convierte en tarea (`T*`) o en un spec nuevo.
6. Si hay una fuga activa, **no publicar el informe** hasta rotar el secreto.

```bash
python specs/tools/code_metrics.py
python specs/tools/scan_secrets.py
python specs/tools/scan_secrets.py --history
python specs/tools/check_dependencies.py --strict
pip-audit -r requirements.txt
cd syntax_sprint && python manage.py check --deploy
```

> Línea base: `audits/code/2026-11-10-linea-base.md` (3.8/10, F) y
> `audits/security/2026-11-10-linea-base.md` (CRÍTICO). Ver la sección 8.

## 11. Despliegue en Render

| Aspecto | Valor |
| --- | --- |
| Hosting | Render Web Service |
| URL | `https://syntaxsprint.onrender.com/` |
| Estado | Live verificado (2026-11-10) |
| Región | `gcp-us-west1` (Oregón) |
| Base de datos | InsForge PostgreSQL (`eu-central`) vía `DATABASE_URL` |
| Estáticos | WhiteNoise + `collectstatic` |
| Build | `pip install -r requirements.txt && python syntax_sprint/manage.py collectstatic --noinput` |
| Start | `python syntax_sprint/manage.py migrate --noinput && gunicorn --chdir syntax_sprint syntax_sprint.wsgi:application --bind 0.0.0.0:$PORT` |
| Guía | `DEPLOY.md` |
| Blueprint | `render.yaml` |

Reglas:

1. La `SECRET_KEY` se rota en Render → Environment, no en GitHub.
2. Antes de mergear/pushear a `main`, haz backup de la base: Render redepliega
   automáticamente y un SQLite sin disco persistente se pierde.
3. `ALLOWED_HOSTS` no lleva esquema ni barra final.
4. `TRUST_PROXY_HEADERS=True` es obligatorio detrás del proxy de Render.
5. No subir `.env`, `db.sqlite3`, `staticfiles/` ni `backup.json`.
6. Si cambias clases de Tailwind, ejecuta `npm run build:css` y commitea
   `syntax_sprint/static/css/tailwind.css`.

## 12. Referencias

- `README.md` — descripción funcional e instalación.
- `DEPLOY.md` — guía de despliegue en Render.
- `render.yaml` — blueprint de Render.
- `specs/README.md` — manual de SDD.
- `specs/constitution.md` — principios no negociables.
- `specs/traceability.md` — requisito → tarea → verificación.
- `specs/000-overview/plan.md` — arquitectura y ADRs.
- `specs/templates/audit-report.md` — plantilla de informes de auditoría.
- `specs/010-dependencies/spec.md` — procedimiento de actualización de dependencias.
- `audits/README.md` — histórico de auditorías.
