from .base import *

INSTALLED_APPS += ('django_extensions',)
ALLOWED_HOSTS = ["10.0.0.77"]

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

TRANSACTIONS_URL = "http://10.0.0.77/transactions/"
