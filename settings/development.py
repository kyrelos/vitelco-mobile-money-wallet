from .base import *

INSTALLED_APPS += ('django_extensions',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'vitelco',
        'USER': 'vitelco',
        'ADMINUSER': 'postgres',
        'PASSWORD': 'secretpassword',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
