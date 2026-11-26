# Despliegue en Render

Guía operativa de SyntaxSprint. El código vive en GitHub (público) y la aplicación
se ejecuta en **Render** como Web Service.

## 1. Stack y ubicación

| Elemento | Valor |
| --- | --- |
| URL | `https://syntaxsprint.onrender.com/` |
| Región | `gcp-us-west1` (Oregón) |
| Runtime | Python 3.12 |
| Servidor | Gunicorn |
| Base de datos | Neon PostgreSQL (`eu-central`) |
| Estáticos | WhiteNoise + `collectstatic` |
| Repositorio | `Chorexxs/SyntaxSprint` (público) |
| Plan | Free (la instancia se duerme por inactividad) |

> El DNS `syntaxsprint.onrender.com` apunta a Render. Si el servicio no responde,
> revisa **Logs** y **Events** en el dashboard: puede estar dormido, suspendido o
> eliminado.

## 2. Variables de entorno

Render Dashboard → servicio `syntaxsprint` → **Environment**.

| Variable | Valor | Obligatoria |
| --- | --- | --- |
| `SECRET_KEY` | Clave aleatoria ≥ 50 caracteres | Sí |
| `DEBUG` | `False` | Sí |
| `ALLOWED_HOSTS` | `syntaxsprint.onrender.com` | Sí |
| `CSRF_TRUSTED_ORIGINS` | `https://syntaxsprint.onrender.com` | Sí |
| `TRUST_PROXY_HEADERS` | `True` | Sí |
| `DATABASE_URL` | Cadena Postgres agrupada de Neon (`sslmode=require`) | Sí |
| `DATABASE_URL_UNPOOLED` | Cadena directa de Neon (migraciones y `createcachetable`) | Sí |
| `RATE_LIMIT_CACHE_ALIAS` | `shared` (caché de BD entre workers) | Recomendada |
| `SNIPPET_RATE_LIMIT_CACHE_ALIAS` | `default` (LocMem por worker) | Opcional |
| `ADMIN_TOTP_REQUIRED` | `False` hasta enrolar el admin | Opcional |
| `PYTHON_VERSION` | `3.12` | Opcional |

Reglas:

- `ALLOWED_HOSTS` **no** lleva `https://` ni barra final.
- `TRUST_PROXY_HEADERS=True` evita bucles de redirección HTTPS en Render.
- Nunca pongas estos valores en GitHub, `README.md` ni `render.yaml` (salvo los que
  ya son públicos).

## 3. Rotar `SECRET_KEY`

1. Genera una clave nueva:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(64))"
   ```

2. Render Dashboard → `syntaxsprint` → **Environment**.
3. Edita `SECRET_KEY` y pega la clave.
4. **Save Changes**. Render redepliega automáticamente.
5. Borra las sesiones y resetea contraseñas (sección 6).

La `SECRET_KEY` invalida tokens firmados, pero **no** borra las sesiones guardadas
en la base de datos: hay que eliminarlas aparte.

## 4. Base de datos (Neon PostgreSQL)

La base de datos es el proyecto **SyntaxSprint** de **Neon**
(`flat-silence-32183356`, rama `production`, región `eu-central`), declarado en
`neon.ts` y provisionado con `neon deploy`.

Neon entrega dos cadenas para la misma base:

| Variable | Tipo | Uso |
| --- | --- | --- |
| `DATABASE_URL` | Agrupada (`-pooler`, PgBouncer) | Tráfico de la aplicación |
| `DATABASE_URL_UNPOOLED` | Directa | `migrate`, `test`, `flush`, `dbshell`, `createcachetable` |

`settings.py` elige la directa sola cuando el comando de `manage.py` está en
`DIRECT_DB_COMMANDS`; PgBouncer en modo transacción no conserva estado de sesión y
puede romper migraciones y dumps.

1. Vuelca las variables del proyecto vinculado (`.neon`):

   ```bash
   neon env pull
   ```

   Escribe `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `NEON_BRANCH` y
   `NEON_BRANCH_ID` en `.env` (ignorado por git). Cópialas a Render →
   **Environment** como `DATABASE_URL` y `DATABASE_URL_UNPOOLED`; nunca las subas
   al repositorio.

2. El Start Command ejecuta `migrate` y `createcachetable` en cada deploy (la tabla
   de caché compartida del rate limiting). También puedes hacerlo a mano:

   ```bash
   python syntax_sprint/manage.py migrate --noinput
   python syntax_sprint/manage.py createcachetable
   ```

3. Verifica las tablas:

   ```bash
   psql "$DATABASE_URL_UNPOOLED" -c '\dt'
   ```

   o `neon inspect db table-sizes`.

### Migrar datos desde SQLite

```bash
# 1. Backup local
python syntax_sprint/manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission > backup.json

# 2. Configura DATABASE_URL / DATABASE_URL_UNPOOLED (Neon) y aplica migraciones
python syntax_sprint/manage.py migrate --noinput
python syntax_sprint/manage.py createcachetable

# 3. Carga los datos
python syntax_sprint/manage.py loaddata backup.json
```

> `backup.json` contiene usuarios y hashes de contraseña. No lo subas a GitHub.
> La app también puede usar SQLite en local (`DB_PATH`), pero producción usa
> Neon.

> Latencia: Render está en `oregon` y Neon en `eu-central`. Si importa, mueve el
> Web Service a una región europea.

## 5. Build y arranque

En Render → **Settings**:

| Campo | Valor |
| --- | --- |
| Build Command | `pip install -r requirements.txt && python syntax_sprint/manage.py collectstatic --noinput` |
| Start Command | `python syntax_sprint/manage.py migrate --noinput && python syntax_sprint/manage.py createcachetable && gunicorn --chdir syntax_sprint syntax_sprint.wsgi:application --bind 0.0.0.0:$PORT` |
| Health Check Path | `/healthz` |

El repositorio incluye `render.yaml` como blueprint. Si el servicio ya existe, el
blueprint no se aplica solo: revisa que los comandos y variables coincidan. El
servicio de producción se reconcilió a mano el **2026-11-26**: `healthCheckPath`
pasó de `/` a `/healthz` y el Start Command incorporó `createcachetable`.

> `createcachetable` es idempotente: si la tabla ya existe imprime
> `Cache table 'syntax_sprint_cache' already exists.` y termina con código 0, así
> que no rompe el arranque. La tabla la usa `RATE_LIMIT_CACHE_ALIAS=shared`.
>
> `/healthz` ejecuta `SELECT 1` y devuelve 503 si la base no responde. Como es el
> health check de Render, un deploy que no pueda hablar con Neon no llega a `live`
> y se revierte solo, en lugar de dejar el servicio en verde sin base de datos.

> Las migraciones se ejecutan en el Start Command. No se ejecutan al importar
> `wsgi.py` para evitar que el worker se quede bloqueado si la base de datos no
> responde.

## 6. Después de rotar la clave

### Borrar sesiones

```bash
# Render Shell o Job
python syntax_sprint/manage.py clearsessions
```

Si no tienes Shell, usa un **Job** puntual con el mismo comando o elimina las filas
de `django_session` desde el panel de PostgreSQL.

### Resetear contraseñas

```bash
python syntax_sprint/manage.py changepassword <usuario>
```

Repite para las 6 cuentas afectadas. Si no tienes Shell, crea un superusuario y usa
`/admin/`, o ejecuta un Job.

## 7. Estáticos

El proyecto usa WhiteNoise:

- `WhiteNoiseMiddleware` sirve los archivos de `staticfiles/`.
- `collectstatic` se ejecuta en el build.
- `STORAGES["staticfiles"]` usa `CompressedStaticFilesStorage`.
- `WHITENOISE_USE_FINDERS=True` sirve desde `STATICFILES_DIRS` aunque el build
  no ejecute `collectstatic`.

Verificación:

```bash
python syntax_sprint/manage.py collectstatic --noinput
python syntax_sprint/manage.py findstatic css/styles.css --verbosity 2
curl -I https://syntaxsprint.onrender.com/static/css/styles.css
```

Si devuelve 404:

1. Confirma que el build ejecuta `collectstatic`.
2. Confirma que `WhiteNoiseMiddleware` está justo después de `SecurityMiddleware`.
3. Revisa los logs del build.

## 8. Checklist de despliegue

- [ ] Backup de la base de datos.
- [ ] `SECRET_KEY` nueva en Render.
- [ ] `DEBUG=False`.
- [ ] `ALLOWED_HOSTS` sin esquema ni barra final.
- [ ] `CSRF_TRUSTED_ORIGINS` con `https://`.
- [ ] `TRUST_PROXY_HEADERS=True`.
- [ ] `DATABASE_URL` y `DATABASE_URL_UNPOOLED` de Neon.
- [ ] `collectstatic` en el build.
- [ ] `healthCheckPath` = `/healthz` (consulta la base).
- [ ] Migraciones aplicadas.
- [ ] Sesiones borradas.
- [ ] Contraseñas reseteadas.
- [ ] `/`, `/login`, `/static/css/styles.css` y `/admin/` responden.
- [ ] Logs sin errores 500.

## 9. Errores comunes

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| `DisallowedHost` | `ALLOWED_HOSTS` con esquema o vacío | `syntaxsprint.onrender.com` |
| `ModuleNotFoundError: No module named 'backend'` | Start Command antiguo sin `--chdir` | Usar `gunicorn --chdir syntax_sprint ...` o el fallback de `wsgi.py` |
| `No open ports detected` | Gunicorn escuchando en `127.0.0.1:8000` | `gunicorn.conf.py` o `--bind 0.0.0.0:$PORT` |
| Render dice "live" pero todo da timeout | Worker bloqueado (migración en import o BD inaccesible) | Revisar Start Command y logs; no migrar en `wsgi.py` |
| `CSRF verification failed` | Origen no confiable | `CSRF_TRUSTED_ORIGINS=https://...` |
| Bucle de redirección HTTPS | Proxy no reconocido | `TRUST_PROXY_HEADERS=True` |
| CSS/JS 404 | Sin `collectstatic` o sin WhiteNoise | Revisar build y middleware |
| Datos desaparecen tras deploy | `DATABASE_URL` no configurada | Configurar Neon |
| `connection refused` a Neon | `DATABASE_URL` incorrecta o compute suspendido | `neon env pull` y revisar `neon postgres computes list` |
| `password authentication failed` | Credenciales de Neon obsoletas | Volver a ejecutar `neon env pull` y actualizar Render |
| `prepared statement ... already exists` o `relation ... does not exist` en migraciones | Migración por la conexión agrupada | Configurar `DATABASE_URL_UNPOOLED` |
| `remaining connection slots are reserved` | Demasiadas conexiones directas | Usar la cadena agrupada (`-pooler`) en `DATABASE_URL` |
| El deploy no llega a `live` y el log repite `health check` | `/healthz` devuelve 503 porque la base no responde | Revisar `DATABASE_URL`, la suspensión del compute en Neon y los logs del servicio |
| `createcachetable` falla en el arranque | Sin permisos DDL o conexión agrupada | Ejecutarlo con `DATABASE_URL_UNPOOLED`; en Render basta con tenerla configurada |
| Servicio no responde | Free dormido, crash o suspendido | Revisar Logs/Events |

## 10. Rollback

1. Render → **Deploys** → selecciona el deploy anterior → **Rollback**.
2. Si el cambio incluía migraciones incompatibles, restaura el backup de la base.
3. No hagas force-push a `main` para revertir: usa un commit de reversión.

## 11. Seguridad

- No versionar `.env`, `db.sqlite3`, `staticfiles/`, `backup.json`, `.neon` ni `.insforge/`.
- Rotar cualquier secreto que haya estado en un repo público.
- El repositorio es **público**: nunca subas secretos y, si se filtra uno, rota la
  credencial; purgar el historial no recupera un secreto ya publicado.
- Si hay una fuga activa, pasa el repositorio a privado hasta rotar y purgar, y no
  publiques el informe (`specs/009-cybersecurity`).
- Revisar `audits/security/` antes de cada despliegue grande.

### Activar la 2FA del admin

1. En Render → **Shell** (o en local con la `DATABASE_URL` de producción):

   ```bash
   python syntax_sprint/manage.py enroll_admin_totp --username <staff> --write /tmp/totp.txt
   ```

   El comando **no imprime el secreto**: lo guarda en el archivo indicado con permisos
   `0600`. Añádelo a la app de autenticación y bórralo (`rm /tmp/totp.txt`). Recuerda
   que la Shell de Render registra lo que muestres en pantalla: evita `cat` en claro o
   rota el secreto si sospechas que quedó en los logs.

2. Cambia `ADMIN_TOTP_REQUIRED` a `True` en Render → **Environment**.
3. Entra en `/admin/`: pedirá el código de 6 dígitos.
4. Para desactivarlo: `enroll_admin_totp --username <staff> --disable` y pon la
   variable a `False`.

> Si se activa sin enrolar, el admin queda bloqueado (403 con instrucciones). El
> comando de desactivación se puede ejecutar desde la Shell de Render sin pasar por
> la web.

## 12. Despliegue alternativo en Vercel

URL de producción: `https://syntax-sprint-ten.vercel.app`

Vercel detecta Django por `syntax_sprint/manage.py` y resuelve la entrada desde
`WSGI_APPLICATION`. Para que el build no falle:

1. `.python-version` debe ser `3.12` (Vercel no dispone del parche exacto `3.12.1`).
2. En Vercel → Settings → Environment Variables:
   - `SECRET_KEY` y `DEBUG=False`.
   - `DATABASE_URL` y `DATABASE_URL_UNPOOLED` de Neon.
   - `CSRF_TRUSTED_ORIGINS=https://<dominio>.vercel.app`.
   - `TRUST_PROXY_HEADERS=True` y `RATE_LIMIT_CACHE_ALIAS=shared`.
   - `SNIPPET_RATE_LIMIT_CACHE_ALIAS=default` y `ADMIN_TOTP_REQUIRED=False`.
   - **Define `SECRET_KEY` también en el entorno `Preview`.** El build carga
     `settings.py` y falla con `UndefinedValueError` (o el mensaje
     `Falta la variable de entorno SECRET_KEY`) si el entorno no la tiene. Las
     ramas y los PRs (incluidos los de Dependabot) generan despliegues de
     Preview, así que la variable debe existir en `Production` y en `Preview`
     por separado. Usa una clave distinta para Preview:
     `python -c "import secrets;print(secrets.token_urlsafe(64))" | vercel env add SECRET_KEY preview`.
     Los Preview usan una rama de Neon propia (ver más abajo), nunca la base de
     producción.
3. Vercel añade solo `VERCEL_URL` y el dominio de producción a `ALLOWED_HOSTS` y
   `CSRF_TRUSTED_ORIGINS`.
4. `collectstatic` se ejecuta automáticamente al detectar `STATIC_ROOT`.
5. Las migraciones no se ejecutan en el build: aplícalas antes con la
   `DATABASE_URL_UNPOOLED` de Neon (desde local con tu `.env` o desde la Shell de
   Render). `vercel env pull` no sirve para esto porque los valores son Secret.
6. En Vercel las conexiones no se reutilizan (`conn_max_age=0`) para no agotar el
   pool de PostgreSQL.
7. Los despliegues con **Vercel CLI** (`vercel deploy`) **no aplican `.gitignore`**:
   suben `.env`, `.neon`, `.insforge/` y `*.sqlite3` si no están excluidos. El
   repositorio incluye un `.vercelignore` para impedirlo; no lo elimines. Antes de
   desplegar, comprueba que no se cuelan secretos:
   `vercel deploy --dry --json` no debe listar `.env`, `.neon`, `.insforge` ni bases
   SQLite. Los despliegues desde Git (ramas y PRs) sí respetan `.gitignore`, y por
   eso Preview necesita sus propias variables de entorno.

### Estado y actualización (2026-11-26)

Las variables de `Production` se migraron de InsForge a Neon el **2026-11-26** y se
verificaron con una prueba real contra `https://syntax-sprint-ten.vercel.app`
(signup, resultado, perfil, logout y `/healthz`). El usuario de prueba se creó en
Neon y se borró al terminar.

Las variables están guardadas como **Secret**: `vercel env pull` escribe
`[SENSITIVE]` en lugar del valor, así que no se pueden leer desde la CLI. Para
rotarlas sin exponerlas en la línea de comandos, pasa el valor por stdin:

```bash
vercel env add DATABASE_URL --environment production --force --sensitive
# pega el valor o redirige desde tu .env local
```

Un cambio de variables **no se aplica solo**: hace falta un despliegue nuevo
(`git push` a `main` o `vercel redeploy <deployment-url> --environment production`).

### Preview con base de datos propia (rama de Neon)

Los despliegues de Preview usan una rama de Neon independiente para no escribir en
los datos de producción: rama **`preview`** (`br-mute-voice-bg3gzv33`), hija de
`production`. Desde el 2026-11-26 el entorno `Preview` de Vercel tiene
`DATABASE_URL` (agrupada) y `DATABASE_URL_UNPOOLED` (directa) apuntando a esa rama,
ambas como Secret.

Para recrearla o refrescarla:

```bash
neon branch create --name preview --parent production --no-secrets
neon env pull --branch preview --env DATABASE_URL --env DATABASE_URL_UNPOOLED \
  --file /tmp/neon_preview.env
grep '^DATABASE_URL=' /tmp/neon_preview.env | cut -d= -f2- \
  | vercel env add DATABASE_URL --environment preview --force --sensitive
grep '^DATABASE_URL_UNPOOLED=' /tmp/neon_preview.env | cut -d= -f2- \
  | vercel env add DATABASE_URL_UNPOOLED --environment preview --force --sensitive
```

La rama copia esquema y datos de `production` en el momento de crearse; no hace
falta migrar. Un `git push` solo actualiza producción: para ver los cambios en un
Preview hay que desplegar (`vercel deploy`) o abrir un PR.

> Los Preview están protegidos por **Vercel Authentication**. Para probarlos por HTTP
> usa `vercel curl <url>` o ejecuta el cliente dentro de `vercel env run` y envía el
> header `x-vercel-trusted-oidc-idp-token` con `VERCEL_OIDC_TOKEN` (el de
> `.env.local`, que se refresca con `vercel env pull .env.local --yes`). No desactives
> Deployment Protection para que pasen las pruebas.

## 13. Keep-alive del tier gratuito de Render

Render duerme el Web Service tras **15 minutos sin tráfico**. El workflow
`.github/workflows/keepalive.yml` genera actividad tres veces por semana (lunes,
miércoles y viernes a las 06:17 UTC) para que el servicio no acumule días dormido.

Neon **no necesita keep-alive**: su compute se suspende por inactividad y se
reanuda solo con la siguiente consulta, sin pausar el proyecto ni borrar datos.
Por eso el workflow ya no consulta la base por `psql`.

| Job | Qué hace | Requisito |
| --- | --- | --- |
| `Prueba de vida de Render` | `GET /` y `GET /healthz`, que ejecuta `SELECT 1` | ninguno |

### Configuración (una sola vez)

1. Actions → **Keep-alive** → **Run workflow** para la primera ejecución manual.

Si un job falla, GitHub avisa por email al autor del cron y el fallo queda en
**Actions**. Ese aviso es la señal de que el keep-alive ha dejado de funcionar.
GitHub puede retrasar los crons varias horas (el 2026-11-19 se ejecutó a las 15:50
UTC, casi 10 h después de lo previsto); por eso hay tres ejecuciones semanales.

### Qué no hace

- **No despliega**: Render no suspende por falta de deploys, solo por agotar las
  750 h de instancia del *workspace* o el ancho de banda del plan Free. Consulta
  el consumo en Render → **Billing → Monthly Included Usage**.
- No mantiene Render despierto: el servicio vuelve a dormirse a los 15 minutos.
  Es lo esperado; la primera visita tarda ~1 minuto en despertarlo.
- No sustituye a `purge_analytics` si la base se acerca al límite de almacenamiento
  del plan Free de Neon. Comprueba el uso con `neon inspect db table-sizes`.
- No reactiva un compute suspendido por cuota agotada: revisa **Billing** en Neon
  y espera al siguiente ciclo o cambia de plan.

