from urllib.parse import quote

from .countries import TRAVEL_COUNTRIES


def site_contact(request):
    whatsapp_number = '96176832813'
    general_message = "Hello, I'd like to inquire about Sama Tours services."
    return {
        'SITE_EMAIL': 'info@samatourslb.com',
        'SITE_PHONE': '+961 25 450 473',
        'SITE_PHONE_ALT': '+961 25 954 473',
        'SITE_WHATSAPP': '+961 76 832 813',
        'SITE_WHATSAPP_NUMBER': whatsapp_number,
        'TRAVEL_COUNTRIES': TRAVEL_COUNTRIES,
        'SITE_ADDRESS': (
            'Sama Tours, Gallerie Semaan Crossroad, Hazmieh Highway, '
            'Hyundai Car Showroom Building, 1st Floor, Hazmieh'
        ),
        'SITE_FACEBOOK': 'https://www.facebook.com/',
        'SITE_INSTAGRAM': 'https://www.instagram.com/',
        'SITE_WHATSAPP_URL': f'https://wa.me/{whatsapp_number}?text={quote(general_message)}',
        'GOOGLE_MAPS_EMBED': (
            'https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3315.2!2d35.52!3d33.85!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zSGF6bWllaWUsIExlYmFub24!5e0!3m2!1sen!2slb!4v1'
        ),
    }
