# Despliegue en Render

Guía operativa de SyntaxSprint. El código vive en GitHub (privado) y la aplicación
se ejecuta en **Render** como Web Service.

## 1. Stack y ubicación

| Elemento | Valor |
| --- | --- |
| URL | `https://syntaxsprint.onrender.com/` |
| Región | `gcp-us-west1` (Oregón) |
| Runtime | Python 3.12 |
| Servidor | Gunicorn |
| Base de datos | InsForge PostgreSQL (`eu-central`) |
| Estáticos | WhiteNoise + `collectstatic` |
| Repositorio | `Chorexxs/SyntaxSprint` (privado) |
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
| `DATABASE_URL` | Cadena Postgres de InsForge (`sslmode=require`) | Sí |
| `RATE_LIMIT_CACHE_ALIAS` | `shared` (caché de BD entre workers) | Recomendada |
| `ADMIN_TOTP_REQUIRED` | `False` hasta enrolar el admin | Opcional |
| `PYTHON_VERSION` | `3.12.1` | Opcional |

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

## 4. Base de datos (InsForge PostgreSQL)

La base de datos es un proyecto de **InsForge** en la región `eu-central`.

1. Obtén la cadena de conexión con la CLI actualizada (>= 0.2.8):

   ```bash
   npx -y @insforge/cli@latest db connection-string
   ```

   > La versión 0.1.x devolvía una contraseña inválida para `postgres`.
   > Si no conecta, actualiza la CLI o copia la cadena desde el dashboard de
   > InsForge (Database → Connect).

2. Añádela en Render → servicio `syntaxsprint` → **Environment** como
   `DATABASE_URL`. Debe incluir `?sslmode=require`.

3. El Start Command ejecuta `migrate` y `createcachetable` en cada deploy (la tabla
   de caché compartida del rate limiting). También puedes hacerlo a mano:

   ```bash
   python syntax_sprint/manage.py migrate --noinput
   python syntax_sprint/manage.py createcachetable
   ```

4. Verifica las tablas:

   ```bash
   npx -y @insforge/cli@latest db tables
   ```

### Migrar datos desde SQLite

```bash
# 1. Backup local
python syntax_sprint/manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission > backup.json

# 2. Configura DATABASE_URL (InsForge) y aplica migraciones
python syntax_sprint/manage.py migrate --noinput
python syntax_sprint/manage.py createcachetable

# 3. Carga los datos
python syntax_sprint/manage.py loaddata backup.json
```

> `backup.json` contiene usuarios y hashes de contraseña. No lo subas a GitHub.
> La app también puede usar SQLite en local (`DB_PATH`), pero producción usa
> InsForge.

> Latencia: Render está en `oregon` e InsForge en `eu-central`. Si importa,
> mueve el Web Service a una región europea.

## 5. Build y arranque

En Render → **Settings**:

| Campo | Valor |
| --- | --- |
| Build Command | `pip install -r requirements.txt && python syntax_sprint/manage.py collectstatic --noinput` |
| Start Command | `python syntax_sprint/manage.py migrate --noinput && python syntax_sprint/manage.py createcachetable && gunicorn --chdir syntax_sprint syntax_sprint.wsgi:application --bind 0.0.0.0:$PORT` |
| Health Check Path | `/` |

El repositorio incluye `render.yaml` como blueprint. Si el servicio ya existe, el
blueprint no se aplica solo: revisa que los comandos y variables coincidan.

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
- [ ] `DATABASE_URL` de InsForge.
- [ ] `collectstatic` en el build.
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
| Datos desaparecen tras deploy | `DATABASE_URL` no configurada | Configurar InsForge |
| `connection refused` a InsForge | `DATABASE_URL` incorrecta | Usar la cadena de `db connection-string` (CLI >= 0.2.8) |
| `password authentication failed` | Credenciales InsForge obsoletas | Actualizar la CLI a 0.2.8+, re-link o copiar la cadena del dashboard |
| Servicio no responde | Free dormido, crash o suspendido | Revisar Logs/Events |

## 10. Rollback

1. Render → **Deploys** → selecciona el deploy anterior → **Rollback**.
2. Si el cambio incluía migraciones incompatibles, restaura el backup de la base.
3. No hagas force-push a `main` para revertir: usa un commit de reversión.

## 11. Seguridad

- No versionar `.env`, `db.sqlite3`, `staticfiles/`, `backup.json` ni `.insforge/`.
- Rotar cualquier secreto que haya estado en un repo público.
- Mantener el repositorio privado hasta que la rotación esté completa.
- Revisar `audits/security/` antes de cada despliegue grande.

### Activar la 2FA del admin

1. En Render → **Shell** (o en local con la `DATABASE_URL` de producción):

   ```bash
   python syntax_sprint/manage.py enroll_admin_totp --username <staff>
   ```

   El comando imprime el secreto y la URI `otpauth://`. Añádelo a la app de
   autenticación y limpia la terminal.

2. Cambia `ADMIN_TOTP_REQUIRED` a `True` en Render → **Environment**.
3. Entra en `/admin/`: pedirá el código de 6 dígitos.
4. Para desactivarlo: `enroll_admin_totp --username <staff> --disable` y pon la
   variable a `False`.

> Si se activa sin enrolar, el admin queda bloqueado (403 con instrucciones). El
> comando de desactivación se puede ejecutar desde la Shell de Render sin pasar por
> la web.
