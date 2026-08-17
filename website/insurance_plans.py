"""Travel insurance plan copy — keyed by plan name (API returns names/prices only)."""

from __future__ import annotations

from typing import Any

from django.utils.translation import gettext as _

from .insurance_filters import classify_plan, format_insurance_price

# Match plan name (case-insensitive substring) → marketing copy msgids (English).
# More specific names first (sport / cov variants before base tiers).
PLAN_COPY: list[tuple[str, dict[str, Any]]] = [
    ('going basic cov plus sport', {
        'summary': 'Basic cover with COVID-19 and sport activity protection.',
        'benefits': [
            'Emergency medical expenses abroad',
            'COVID-19 medical cover (where applicable)',
            'Sport & adventure activity cover',
            'Medical repatriation',
            '24/7 travel assistance hotline',
        ],
    }),
    ('going advanced plus sport', {
        'summary': 'Advanced cover with sport and adventure activity protection.',
        'benefits': [
            'Emergency medical & hospital expenses abroad',
            'Sport & adventure activity cover',
            'Medical repatriation & emergency evacuation',
            'Trip cancellation & interruption',
            '24/7 travel assistance hotline',
        ],
    }),
    ('going advanced cov', {
        'summary': 'Comprehensive cover including COVID-19-related medical expenses.',
        'benefits': [
            'Emergency medical & hospital expenses abroad',
            'COVID-19 medical cover (where applicable)',
            'Medical repatriation & emergency evacuation',
            'Trip cancellation & interruption',
            'Baggage loss or delay',
            '24/7 travel assistance hotline',
        ],
    }),
    ('going advanced', {
        'summary': 'Comprehensive international travel protection without COVID-specific cover.',
        'benefits': [
            'Emergency medical & hospital expenses abroad',
            'Medical repatriation & emergency evacuation',
            'Trip cancellation & interruption',
            'Baggage loss or delay',
            '24/7 travel assistance hotline',
        ],
    }),
    ('going basic cov', {
        'summary': 'Essential protection with COVID-19 medical cover.',
        'benefits': [
            'Emergency medical expenses abroad',
            'COVID-19 medical cover (where applicable)',
            'Medical repatriation',
            'Emergency dental (limited)',
            '24/7 travel assistance hotline',
        ],
    }),
    ('going basic', {
        'summary': 'Essential protection for budget-conscious travellers.',
        'benefits': [
            'Emergency medical expenses abroad',
            'Medical repatriation',
            'Emergency dental (limited)',
            '24/7 travel assistance hotline',
        ],
    }),
    ('going premium', {
        'summary': 'Higher limits and broader protection for international travel.',
        'benefits': [
            'Emergency medical & dental expenses abroad',
            'Medical repatriation & evacuation',
            'Trip delay & missed connection',
            'Personal liability cover',
            '24/7 travel assistance hotline',
        ],
    }),
    ('gold', {
        'summary': 'Premium tier with enhanced medical limits.',
        'benefits': [
            'High-limit emergency medical cover',
            'Medical repatriation & evacuation',
            'Trip cancellation cover',
            'Baggage & personal effects',
            '24/7 assistance',
        ],
    }),
    ('silver', {
        'summary': 'Balanced cover for leisure and business trips.',
        'benefits': [
            'Emergency medical expenses',
            'Medical repatriation',
            'Trip interruption',
            '24/7 assistance',
        ],
    }),
]

DEFAULT_COPY = {
    'summary': 'Travel medical and assistance cover for your trip abroad.',
    'benefits': [
        'Emergency medical expenses while travelling',
        'Medical repatriation assistance',
        '24/7 travel assistance',
        'Full benefits listed in your policy document (PDF)',
    ],
}


def _translate_copy(copy: dict[str, Any]) -> dict[str, Any]:
    return {
        'summary': _(copy['summary']),
        'benefits': [_(benefit) for benefit in copy['benefits']],
    }


def plan_marketing_copy(plan_name: str) -> dict[str, Any]:
    lowered = (plan_name or '').lower()
    for needle, copy in PLAN_COPY:
        if needle in lowered:
            return _translate_copy(copy)
    if 'cov' in lowered:
        translated = _translate_copy(DEFAULT_COPY)
        translated['summary'] = _('Plan includes extended medical cover with COVID-19 protection.')
        translated['benefits'] = translated['benefits'] + [_('COVID-19 related medical cover')]
        return translated
    return _translate_copy(DEFAULT_COPY)


def _plan_badge(plan_name: str) -> str:
    lowered = (plan_name or '').lower()
    if 'sport' in lowered:
        return _('Sport')
    if 'advanced' in lowered:
        return _('Comprehensive')
    if 'premium' in lowered:
        return _('Premium')
    if 'basic' in lowered:
        return _('Essential')
    if 'gold' in lowered:
        return _('Gold')
    if 'silver' in lowered:
        return _('Silver')
    if ' cov' in f' {lowered}' or lowered.endswith('cov'):
        return _('COVID-19')
    return ''


def enrich_offer(offer: dict[str, Any], *, trip_days: int | None = None) -> dict[str, Any]:
    """Add human-readable details to a flattened plan offer."""
    raw = offer.get('raw_plan') or {}
    name = offer.get('name') or raw.get('name') or ''
    copy = plan_marketing_copy(name)

    price_matrix = raw.get('price') or []
    coverage_days = None
    for traveller_prices in price_matrix:
        if isinstance(traveller_prices, list) and traveller_prices:
            row = traveller_prices[0]
            if isinstance(row, dict) and row.get('ConsecutiveDays'):
                coverage_days = int(row['ConsecutiveDays'])
                break

    offer['summary'] = copy['summary']
    offer['benefits'] = copy['benefits']
    offer['full_name'] = raw.get('name') or name
    offer['plan_type'] = raw.get('type') or ''
    offer['badge'] = _plan_badge(name)
    offer['benefit_count'] = len(copy['benefits'])
    classification = classify_plan(name)
    offer['tier'] = classification['tier']
    offer['has_covid'] = classification['has_covid']
    offer['has_sport'] = classification['has_sport']
    currency = offer.get('currency') or 'USD'
    offer['price_display'] = format_insurance_price(currency, offer.get('total_price'))
    if offer.get('total_with_deductible'):
        offer['deductible_price_display'] = format_insurance_price(
            currency, offer.get('total_with_deductible'),
        )
    else:
        offer['deductible_price_display'] = ''
    offer['coverage_days'] = coverage_days
    offer['trip_days'] = trip_days
    offer['has_deductible_option'] = bool(
        offer.get('total_with_deductible') and offer.get('total_without_deductible')
    )
    return offer
