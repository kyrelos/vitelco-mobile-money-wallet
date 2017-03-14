from .base import *

DEBUG = False
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',#'django.db.backends.postgresql_psycopg2',
        'NAME': 'kenblest-geodjango',
        'USER': 'postgres',
        'ADMINUSER':'postgres',
        'PASSWORD': 'to be extracted from environment',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

# Add raven to the list of installed apps
INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': 'https://617e1206fdba4ef7a0e693259a40ffb7:996440c764a840ab83f6fe9bade65ba3@sentry.io/47916',
}