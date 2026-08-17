"""
Local development settings — SQLite, DEBUG on.
"""

from pathlib import Path

from config.env_loader import load_env_file

_BASE_DIR = Path(__file__).resolve().parent.parent.parent
for _env_name in ('.env', 'deploy/production.env'):
    load_env_file(_BASE_DIR / _env_name)

from .base import *  # noqa: F403, E402

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}

DEBUG = True

SECRET_KEY = 'django-insecure-dev-only-not-for-production'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}
