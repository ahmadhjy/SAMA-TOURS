"""
Production settings — all secrets and hosts from environment variables.
Used on PythonAnywhere (see deploy/pythonanywhere_wsgi.py.example).
"""

import os

from .base import *  # noqa: F403
from .base import _env  # noqa: F401

DEBUG = _env('DEBUG', 'DJANGO_DEBUG', default='False').lower() in ('true', '1', 'yes')

SECRET_KEY = _env('SECRET_KEY', 'DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('DJANGO_SECRET_KEY (or SECRET_KEY) must be set in production.')

ALLOWED_HOSTS = [
    host.strip()
    for host in _env('ALLOWED_HOSTS', 'DJANGO_ALLOWED_HOSTS', default='').split(',')
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise ValueError('DJANGO_ALLOWED_HOSTS must be set in production.')

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in _env('CSRF_TRUSTED_ORIGINS', 'DJANGO_CSRF_TRUSTED_ORIGINS', default='').split(',')
    if origin.strip()
]

db_engine = _env('DB_ENGINE', 'DJANGO_DB_ENGINE', default='postgresql')
if db_engine == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': _env('DB_NAME', 'DJANGO_DB_NAME'),
            'USER': _env('DB_USER', 'DJANGO_DB_USER'),
            'PASSWORD': _env('DB_PASSWORD', 'DJANGO_DB_PASSWORD'),
            'HOST': _env('DB_HOST', 'DJANGO_DB_HOST'),
            'PORT': _env('DB_PORT', 'DJANGO_DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        }
    }

# Whitenoise for static files on PythonAnywhere
MIDDLEWARE = list(MIDDLEWARE)  # noqa: F405
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        # Avoid manifest errors if collectstatic was skipped or incomplete on PA
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
