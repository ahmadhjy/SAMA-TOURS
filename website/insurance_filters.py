"""Client-side and server-side filters for travel insurance plan results."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django.utils.translation import gettext_lazy as _

SORT_OPTIONS = [
    ('price_asc', _('Price: low to high')),
    ('price_dsc', _('Price: high to low')),
    ('name_asc', _('Name: A–Z')),
    ('name_dsc', _('Name: Z–A')),
]

TIER_OPTIONS = [
    ('', _('All tiers')),
    ('basic', _('Basic')),
    ('premium', _('Premium')),
    ('advanced', _('Advanced')),
    ('gold', _('Gold')),
    ('silver', _('Silver')),
]

COVID_OPTIONS = [
    ('', _('All plans')),
    ('yes', _('With COVID cover')),
    ('no', _('Without COVID cover')),
]

SPORT_OPTIONS = [
    ('', _('All plans')),
    ('yes', _('With sport cover')),
    ('no', _('Without sport cover')),
]

CURRENCY_OPTIONS_BASE = [
    ('', _('All currencies')),
]

MAX_PRICE_OPTIONS = [
    ('', _('Any price')),
    ('25', _('Up to 25')),
    ('50', _('Up to 50')),
    ('100', _('Up to 100')),
    ('200', _('Up to 200')),
    ('500', _('Up to 500')),
]


def classify_plan(name: str) -> dict[str, Any]:
    lowered = (name or '').lower()
    has_sport = 'sport' in lowered
    # "Cov" as a product suffix (Going Basic Cov), not substring noise
    has_covid = (
        ' cov' in f' {lowered}'
        or lowered.endswith('cov')
        or 'cov plus' in lowered
        or 'cov ' in lowered
    )
    tier = ''
    for needle in ('advanced', 'premium', 'basic', 'gold', 'silver'):
        if needle in lowered:
            tier = needle
            break
    return {'tier': tier, 'has_covid': has_covid, 'has_sport': has_sport}


def format_insurance_price(currency: str, amount: float | Decimal | None) -> str:
    if amount is None:
        return ''
    code = (currency or 'USD').upper()
    value = float(amount)
    prefix_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'AUD': 'A$',
        'CAD': 'C$',
    }
    if code in prefix_symbols:
        return f'{prefix_symbols[code]}{value:,.2f}'
    return f'{code} {value:,.2f}'


def parse_insurance_filters(params) -> dict[str, str]:
    get = params.get if hasattr(params, 'get') else params.__getitem__
    return {
        'tier': (get('tier') or '').strip().lower(),
        'covid': (get('covid') or '').strip().lower(),
        'sport': (get('sport') or '').strip().lower(),
        'currency': (get('currency') or '').strip().upper(),
        'sort': (get('sort') or 'price_asc').strip(),
        'q': (get('q') or '').strip().lower(),
        'max_price': (get('max_price') or '').strip(),
        'min_price': (get('min_price') or '').strip(),
    }


def filters_active(filters: dict[str, str]) -> bool:
    return any(filters.get(key) for key in ('tier', 'covid', 'sport', 'currency', 'q', 'max_price', 'min_price'))


def _decimal(value: str) -> Decimal | None:
    value = (value or '').strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def currency_options_from_offers(offers: list[dict[str, Any]]) -> list[tuple[str, str]]:
    codes = {'USD', 'EUR', 'GBP', 'AUD', 'CAD', 'CHF'}
    for offer in offers:
        code = (offer.get('currency') or '').upper()
        if code:
            codes.add(code)
    options = list(CURRENCY_OPTIONS_BASE)
    for code in sorted(codes):
        options.append((code, code))
    return options


def filter_and_sort_offers(
    offers: list[dict[str, Any]],
    filters: dict[str, str],
) -> tuple[list[dict[str, Any]], int]:
    total = len(offers)
    result = list(offers)

    tier = filters.get('tier', '')
    if tier:
        result = [o for o in result if o.get('tier') == tier]

    covid = filters.get('covid', '')
    if covid == 'yes':
        result = [o for o in result if o.get('has_covid')]
    elif covid == 'no':
        result = [o for o in result if not o.get('has_covid')]

    sport = filters.get('sport', '')
    if sport == 'yes':
        result = [o for o in result if o.get('has_sport')]
    elif sport == 'no':
        result = [o for o in result if not o.get('has_sport')]

    currency = filters.get('currency', '')
    if currency:
        result = [o for o in result if (o.get('currency') or '').upper() == currency]

    query = filters.get('q', '')
    if query:
        result = [
            o for o in result
            if query in (o.get('name') or '').lower()
            or query in (o.get('full_name') or '').lower()
        ]

    max_price = _decimal(filters.get('max_price', ''))
    if max_price is not None:
        result = [o for o in result if Decimal(str(o.get('total_price') or 0)) <= max_price]

    min_price = _decimal(filters.get('min_price', ''))
    if min_price is not None:
        result = [o for o in result if Decimal(str(o.get('total_price') or 0)) >= min_price]

    sort = filters.get('sort', 'price_asc')
    if sort == 'price_dsc':
        result.sort(key=lambda o: o.get('total_price') or 0, reverse=True)
    elif sort == 'name_asc':
        result.sort(key=lambda o: (o.get('name') or '').lower())
    elif sort == 'name_dsc':
        result.sort(key=lambda o: (o.get('name') or '').lower(), reverse=True)
    else:
        result.sort(key=lambda o: o.get('total_price') or 0)

    return result, total


def insurance_filter_context(ctx: dict) -> dict:
    """Template context for advanced plan filters."""
    return {
        'plan_filters': ctx.get('plan_filters') or {},
        'filters_active': ctx.get('filters_active', False),
        'total_plans': ctx.get('total_plans', 0),
        'tier_options': TIER_OPTIONS,
        'covid_options': COVID_OPTIONS,
        'sport_options': SPORT_OPTIONS,
        'sort_options': SORT_OPTIONS,
        'max_price_options': MAX_PRICE_OPTIONS,
        'currency_options': ctx.get('currency_options') or list(CURRENCY_OPTIONS_BASE),
    }
