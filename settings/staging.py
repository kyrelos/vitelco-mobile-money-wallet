from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vitelco',
        'USER': 'vitelco',
        'ADMINUSER': 'postgres',
        'PASSWORD': 'tobeexracted from environment',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

RAVEN_CONFIG = {
    'dsn': 'https://617e1206fdba4ef7a0e693259a40ffb7:996440c764a840ab83f6fe9bade65ba3@sentry.io/47916',
}

# Add raven to the list of installed apps
INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)


