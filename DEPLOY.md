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
| Base de datos | PostgreSQL de Render (recomendado) o SQLite con disco |
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
| `DATABASE_URL` | Cadena de conexión de Render Postgres | Recomendada |
| `PYTHON_VERSION` | `3.12.1` | Opcional |
| `DB_PATH` | `/var/data/db.sqlite3` | Solo SQLite con disco |
| `RUN_MIGRATIONS_ON_START` | `False` si el Start Command ejecuta `migrate`; `True` como fallback | Opcional |

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

## 4. Base de datos

### Opción A — PostgreSQL de Render (recomendada)

Ventajas: persistente, backups, no se pierde en cada deploy.

1. Render Dashboard → **New** → **Postgres** (o aplica `render.yaml`).
2. Copia la **Internal Database URL**.
3. Añádela como `DATABASE_URL` en el Web Service.
4. Ejecuta migraciones:

   ```bash
   python syntax_sprint/manage.py migrate --noinput
   ```

### Opción B — SQLite con disco persistente (plan de pago)

1. Render → servicio → **Disks** → añade un disco de 1 GB en `/var/data`.
2. Añade `DB_PATH=/var/data/db.sqlite3`.
3. Redeploy.
4. Sin disco, el SQLite es efímero y **se pierde en cada deploy**.

### Migrar los datos actuales de SQLite a PostgreSQL

Hazlo **antes** de cambiar `DATABASE_URL` en producción:

```bash
# 1. Backup local (o desde Render Shell)
python syntax_sprint/manage.py dumpdata --natural-foreign --natural-primary \
  -e contenttypes -e auth.Permission > backup.json

# 2. Configura DATABASE_URL y aplica migraciones
python syntax_sprint/manage.py migrate --noinput

# 3. Carga los datos
python syntax_sprint/manage.py loaddata backup.json
```

> `backup.json` contiene usuarios y hashes de contraseña. No lo subas a GitHub.

## 5. Build y arranque

En Render → **Settings**:

| Campo | Valor |
| --- | --- |
| Build Command | `pip install -r requirements.txt && python syntax_sprint/manage.py collectstatic --noinput` |
| Start Command | `python syntax_sprint/manage.py migrate --noinput && gunicorn --chdir syntax_sprint syntax_sprint.wsgi:application --bind 0.0.0.0:$PORT` |
| Health Check Path | `/` |

El repositorio incluye `render.yaml` como blueprint. Si el servicio ya existe, el
blueprint no se aplica solo: revisa que los comandos y variables coincidan.

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
- [ ] `DATABASE_URL` (Postgres) o `DB_PATH` + disco.
- [ ] `collectstatic` en el build.
- [ ] Migraciones aplicadas.
- [ ] `RUN_MIGRATIONS_ON_START=False` si el Start Command ya ejecuta `migrate`.
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
| `CSRF verification failed` | Origen no confiable | `CSRF_TRUSTED_ORIGINS=https://...` |
| Bucle de redirección HTTPS | Proxy no reconocido | `TRUST_PROXY_HEADERS=True` |
| CSS/JS 404 | Sin `collectstatic` o sin WhiteNoise | Revisar build y middleware |
| Datos desaparecen tras deploy | SQLite efímero | Postgres o disco persistente |
| `connection refused` a Postgres | `DATABASE_URL` incorrecta | Usar la Internal URL de Render |
| Servicio no responde | Free dormido, crash o suspendido | Revisar Logs/Events |

## 10. Rollback

1. Render → **Deploys** → selecciona el deploy anterior → **Rollback**.
2. Si el cambio incluía migraciones incompatibles, restaura el backup de la base.
3. No hagas force-push a `main` para revertir: usa un commit de reversión.

## 11. Seguridad

- No versionar `.env`, `db.sqlite3`, `staticfiles/` ni `backup.json`.
- Rotar cualquier secreto que haya estado en un repo público.
- Mantener el repositorio privado hasta que la rotación esté completa.
- Revisar `audits/security/` antes de cada despliegue grande.
