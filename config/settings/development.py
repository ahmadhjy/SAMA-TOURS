"""
Local development settings — SQLite, DEBUG on.
"""

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = 'django-insecure-dev-only-not-for-production'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
    }
}
