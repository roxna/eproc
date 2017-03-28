"""
WSGI config for eProcure project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eProcure.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Whitenoise - to serve staticfiles on Heroku
# Read more: https://devcenter.heroku.com/articles/django-assets
from whitenoise.django import DjangoWhiteNoise
application = DjangoWhiteNoise(application)
