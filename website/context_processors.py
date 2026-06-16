from urllib.parse import quote

from django.conf import settings
from django.urls import translate_url
from django.utils import translation
from django.utils.translation import gettext as _

from .countries import TRAVEL_COUNTRIES


def site_contact(request):
    whatsapp_number = '96176832813'
    general_message = _("Hello, I'd like to inquire about Sama Tours services.")
    return {
        'SITE_EMAIL': 'info@samatourslb.com',
        'SITE_PHONE': '+961 25 450 473',
        'SITE_PHONE_ALT': '+961 25 954 473',
        'SITE_WHATSAPP': '+961 76 832 813',
        'SITE_WHATSAPP_NUMBER': whatsapp_number,
        'TRAVEL_COUNTRIES': TRAVEL_COUNTRIES,
        'SITE_ADDRESS': _(
            'Sama Tours, Gallerie Semaan Crossroad, Hazmieh Highway, '
            'Hyundai Car Showroom Building, 1st Floor, Hazmieh'
        ),
        'SITE_FACEBOOK': 'https://www.facebook.com/samatourlb',
        'SITE_INSTAGRAM': 'https://www.instagram.com/samatourslb/',
        'SITE_WHATSAPP_URL': f'https://wa.me/{whatsapp_number}?text={quote(general_message)}',
        'GOOGLE_MAPS_EMBED': (
            'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3313.2925355168977'
            '!2d35.5247166751683!3d33.85635102804957!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1'
            '!3m3!1m2!1s0x151f1948b6676fcf%3A0xc591964cba708402!2sSama%20Tours'
            '!5e0!3m2!1sen!2slb!4v1781457127223!5m2!1sen!2slb'
        ),
    }


def language_switcher(request):
    current = translation.get_language()
    path = request.get_full_path()
    languages = []
    for code, label in settings.LANGUAGES:
        languages.append({
            'code': code,
            'label': label,
            'url': translate_url(path, code),
            'active': code == current,
        })
    return {'LANGUAGE_SWITCHER': languages, 'CURRENT_LANGUAGE': current}
