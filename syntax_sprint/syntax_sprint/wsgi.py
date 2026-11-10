"""
WSGI config for syntax_sprint project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

# Render may import this module from the repository root. Add the Django
# project directory so that ``backend`` and the inner ``syntax_sprint``
# package are importable regardless of the working directory.
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'syntax_sprint.syntax_sprint.settings')

application = get_wsgi_application()

# Compatibility with the old Render Start Command, which does not run
# migrations. The recommended Start Command runs them explicitly; in that
# case set RUN_MIGRATIONS_ON_START=False.
if os.environ.get("RUN_MIGRATIONS_ON_START", "true").lower() == "true":
    call_command("migrate", interactive=False, verbosity=0)
