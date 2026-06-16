from django.utils.translation import gettext as _, ngettext


WHATSAPP_NUMBER = '96176832813'


def whatsapp_url(message: str, number: str | None = None) -> str:
    from urllib.parse import quote

    return f'https://wa.me/{number or WHATSAPP_NUMBER}?text={quote(message)}'


def quote_request_message(from_place: str, to_place: str, travel_date: str,
                          adults: int, children: int, infants: int) -> str:
    travelers = []
    if adults:
        travelers.append(ngettext('%(count)s adult', '%(count)s adults', adults) % {'count': adults})
    if children:
        travelers.append(ngettext('%(count)s child', '%(count)s children', children) % {'count': children})
    if infants:
        travelers.append(ngettext('%(count)s infant', '%(count)s infants', infants) % {'count': infants})
    traveler_line = ', '.join(travelers) if travelers else _('Not specified')

    return (
        _('Hello Sama Tours! I would like a travel quote.') + '\n\n'
        + _('From: %(place)s') % {'place': from_place} + '\n'
        + _('To: %(place)s') % {'place': to_place} + '\n'
        + _('Travel dates: %(dates)s') % {'dates': travel_date} + '\n'
        + _('Travelers: %(line)s') % {'line': traveler_line} + '\n\n'
        + _('Thank you!')
    )


def package_booking_message(name: str, destination: str, duration: str, price_display: str) -> str:
    return (
        _('Hello Sama Tours! I would like to book a package.') + '\n\n'
        + _('Package: %(name)s') % {'name': name} + '\n'
        + _('Destination: %(dest)s') % {'dest': destination} + '\n'
        + _('Duration: %(duration)s') % {'duration': duration} + '\n'
        + _('Price: %(price)s') % {'price': price_display} + '\n\n'
        + _('Please share availability and payment details. Thank you!')
    )
