import os

from django.core.wsgi import get_wsgi_application

# import admin_service.sentry_init  # ← подключение Sentry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_service.settings")
application = get_wsgi_application()
