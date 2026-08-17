"""
Shared Django settings for Sama Tours website.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _env(*keys, default=None):
    """Read first set environment variable from keys."""
    for key in keys:
        value = os.environ.get(key)
        if value is not None and value != '':
            return value
    return default


INSTALLED_APPS = [
    'jazzmin',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'website',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'website.context_processors.site_contact',
                'website.context_processors.language_switcher',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'Asia/Beirut'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', 'English'),
    ('ar', 'العربية'),
    ('fr', 'Français'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

MODELTRANSLATION_DEFAULT_LANGUAGE = 'en'
MODELTRANSLATION_LANGUAGES = ('en', 'ar', 'fr')
MODELTRANSLATION_FALLBACK_LANGUAGES = {
    'default': ('en',),
    'ar': ('en',),
    'fr': ('en',),
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(_env('MEDIA_ROOT', 'DJANGO_MEDIA_ROOT', default=str(BASE_DIR / 'media')))

# Monty eSIM Reseller API (secrets in .env / deploy/production.env — never commit)
MONTY_ESIM_API_BASE_URL = _env(
    'MONTY_ESIM_API_BASE_URL',
    default='https://resellerapi.montyesim.com/api/v0',
)
MONTY_ESIM_PORTAL_URL = _env(
    'MONTY_ESIM_PORTAL_URL',
    default='https://reseller.montyesim.com/',
)
MONTY_ESIM_USERNAME = _env('MONTY_ESIM_USERNAME', default='')
MONTY_ESIM_PASSWORD = _env('MONTY_ESIM_PASSWORD', default='')
MONTY_ESIM_CURRENCY = _env('MONTY_ESIM_CURRENCY', default='USD')

# Swan IMS v5 — travel insurance (sandbox or production — secrets in .env)
SWAN_IMS_API_BASE_URL = _env(
    'SWAN_IMS_API_BASE_URL',
    default='https://staging.cygnet-ims.com/',
)
SWAN_IMS_USERNAME = _env('SWAN_IMS_USERNAME', default='')
SWAN_IMS_PASSWORD = _env('SWAN_IMS_PASSWORD', default='')
SWAN_IMS_SANDBOX = _env('SWAN_IMS_SANDBOX', default='True').lower() in ('true', '1', 'yes')
SWAN_IMS_DEFAULT_RESIDENCE = _env('SWAN_IMS_DEFAULT_RESIDENCE', default='LBN')
# Block checkout on production until payment gateway is wired (sandbox can stay True)
SWAN_IMS_ALLOW_CHECKOUT = _env('SWAN_IMS_ALLOW_CHECKOUT', default='').lower() in (
    'true', '1', 'yes',
) if _env('SWAN_IMS_ALLOW_CHECKOUT', default='') != '' else SWAN_IMS_SANDBOX

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

JAZZMIN_SETTINGS = {
    'site_title': 'Sama Tours Admin',
    'site_header': 'Sama Tours',
    'site_brand': 'Sama Tours',
    'site_logo': 'media/logo.png',
    'site_logo_classes': 'img-circle',
    'site_icon': 'media/logo.png',
    'welcome_sign': 'Content admin — packages, visas, and bookings',
    'copyright': 'Sama Tours',
    'search_model': ['website.TravelPackage', 'website.VisaRequirement'],
    'user_avatar': None,
    'topmenu_links': [
        {'name': 'View website', 'url': '/', 'new_window': True},
        {'model': 'website.TravelPackage'},
        {'model': 'website.VisaRequirement'},
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'hide_apps': [],
    'hide_models': [],
    'order_with_respect_to': [
        'website',
        'website.TravelPackage',
        'website.VisaRequirement',
        'website.Destination',
        'website.Testimonial',
        'website.EsimOrder',
        'website.TravelInsuranceOrder',
        'auth',
    ],
    'icons': {
        'auth': 'fas fa-users-cog',
        'auth.user': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'website.TravelPackage': 'fas fa-suitcase',
        'website.Destination': 'fas fa-map-marker-alt',
        'website.VisaRequirement': 'fas fa-passport',
        'website.Testimonial': 'fas fa-comment-dots',
        'website.EsimOrder': 'fas fa-sim-card',
        'website.TravelInsuranceOrder': 'fas fa-shield-alt',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'related_modal_active': False,
    'custom_css': 'admin/css/sama_admin.css',
    'custom_js': None,
    'use_google_fonts_cdn': True,
    'show_ui_builder': False,
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {
        'website.travelpackage': 'horizontal_tabs',
        'website.visarequirement': 'horizontal_tabs',
        'auth.user': 'collapsible',
    },
    'language_chooser': False,
}

JAZZMIN_UI_TWEAKS = {
    'navbar_small_text': False,
    'footer_small_text': False,
    'body_small_text': False,
    'brand_small_text': False,
    'brand_colour': 'navbar-navy',
    'accent': 'accent-navy',
    'navbar': 'navbar-navy navbar-dark',
    'no_navbar_border': True,
    'navbar_fixed': True,
    'layout_boxed': False,
    'footer_fixed': False,
    'sidebar_fixed': True,
    'sidebar': 'sidebar-dark-navy',
    'sidebar_nav_small_text': False,
    'sidebar_disable_expand': False,
    'sidebar_nav_child_indent': True,
    'sidebar_nav_compact_style': False,
    'sidebar_nav_legacy_style': False,
    'sidebar_nav_flat_style': False,
    'theme': 'default',
    'dark_mode_theme': None,
    'button_classes': {
        'primary': 'btn-primary',
        'secondary': 'btn-secondary',
        'info': 'btn-info',
        'warning': 'btn-warning',
        'danger': 'btn-danger',
        'success': 'btn-success',
    },
}
