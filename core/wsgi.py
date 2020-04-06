"""
WSGI config for sofokus_django_base project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application

from core.boot_utils import load_django_settings_module

load_django_settings_module()

application = get_wsgi_application()
