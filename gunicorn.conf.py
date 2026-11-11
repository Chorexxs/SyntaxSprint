"""Configuración de Gunicorn para Render y ejecución local.

Gunicorn carga automáticamente `gunicorn.conf.py` desde el directorio de
trabajo. Render expone el puerto en la variable `PORT`; sin este archivo, el
comando antiguo `gunicorn syntax_sprint.syntax_sprint.wsgi:application`
escucharía en `127.0.0.1:8000` y Render no detectaría el puerto.
"""

import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
timeout = 120

# Render solo expone el servicio a través de su proxy, que reescribe
# X-Forwarded-For. Sin esto, `REMOTE_ADDR` sería la IP del proxy y el rate
# limiting del login se compartiría entre todos los usuarios.
forwarded_allow_ips = "*"
