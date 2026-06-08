from urllib.parse import quote

WHATSAPP_NUMBER = '96176832813'


def whatsapp_url(message: str, number: str | None = None) -> str:
    return f'https://wa.me/{number or WHATSAPP_NUMBER}?text={quote(message)}'


def quote_request_message(from_place: str, to_place: str, travel_date: str,
                          adults: int, children: int, infants: int) -> str:
    travelers = []
    if adults:
        travelers.append(f'{adults} adult{"s" if adults != 1 else ""}')
    if children:
        travelers.append(f'{children} child{"ren" if children != 1 else ""}')
    if infants:
        travelers.append(f'{infants} infant{"s" if infants != 1 else ""}')
    traveler_line = ', '.join(travelers) if travelers else 'Not specified'

    return (
        'Hello Sama Tours! I would like a travel quote.\n\n'
        f'From: {from_place}\n'
        f'To: {to_place}\n'
        f'Travel date: {travel_date}\n'
        f'Travelers: {traveler_line}\n\n'
        'Thank you!'
    )


def package_booking_message(name: str, destination: str, duration: str, price_display: str) -> str:
    return (
        'Hello Sama Tours! I would like to book a package.\n\n'
        f'Package: {name}\n'
        f'Destination: {destination}\n'
        f'Duration: {duration}\n'
        f'Price: {price_display}\n\n'
        'Please share availability and payment details. Thank you!'
    )
