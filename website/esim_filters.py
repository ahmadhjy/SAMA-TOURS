"""Parse eSIM search parameters and fetch filtered bundle pages from Monty."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from django.utils.translation import gettext_lazy as _

from .monty_esim import (
    MontyESIMError,
    bundle_data_mb,
    enrich_bundle,
    get_bundles,
    get_cached_countries,
    get_cached_regions,
)

PAGE_SIZE = 50

SORT_OPTIONS = [
    ('price_asc', _('Price: low to high')),
    ('price_dsc', _('Price: high to low')),
    ('data_asc', _('Data: low to high')),
    ('data_dsc', _('Data: high to low')),
    ('bundle_name', _('Name: A–Z')),
]

CATEGORY_OPTIONS = [
    ('country', _('Country plans')),
    ('region', _('Regional plans')),
    ('global', _('Global plans')),
    ('cruise', _('Cruise plans')),
]

PROFILE_OPTIONS = [
    ('', _('Any profile')),
    ('STANDARD', _('Standard eSIM')),
    ('GLOBAL_ESIM', _('Global eSIM profile')),
]

VALIDITY_OPTIONS = [
    ('', _('Any duration')),
    ('7', _('Up to 7 days')),
    ('15', _('Up to 15 days')),
    ('30', _('Up to 30 days')),
    ('90', _('Up to 90 days')),
]

DATA_OPTIONS = [
    ('', _('Any data')),
    ('0.5', _('At least 500 MB')),
    ('1', _('At least 1 GB')),
    ('3', _('At least 3 GB')),
    ('5', _('At least 5 GB')),
    ('10', _('At least 10 GB')),
]

PRICE_MAX_OPTIONS = [
    ('', _('Any price')),
    ('2', _('Up to $2')),
    ('5', _('Up to $5')),
    ('10', _('Up to $10')),
    ('20', _('Up to $20')),
    ('50', _('Up to $50')),
]

VALID_SORTS = {value for value, _ in SORT_OPTIONS}
VALID_CATEGORIES = {value for value, _ in CATEGORY_OPTIONS}
VALID_PROFILES = {value for value, _ in PROFILE_OPTIONS if value}


def _decimal(value: str) -> Decimal | None:
    value = (value or '').strip()
    if not value:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


def _int(value: str) -> int | None:
    value = (value or '').strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _float(value: str) -> float | None:
    value = (value or '').strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_esim_search(request) -> dict[str, Any]:
    sort = (request.GET.get('sort') or 'price_asc').strip()
    if sort not in VALID_SORTS:
        sort = 'price_asc'

    category = (request.GET.get('category') or 'country').strip().lower()
    if category not in VALID_CATEGORIES:
        category = 'country'

    profile_type = (request.GET.get('profile') or '').strip().upper()
    if profile_type and profile_type not in VALID_PROFILES:
        profile_type = ''

    page = _int(request.GET.get('page')) or 1
    page = max(page, 1)

    return {
        'country': (request.GET.get('country') or '').strip().upper(),
        'region': (request.GET.get('region') or '').strip().upper(),
        'q': (request.GET.get('q') or '').strip()[:100],
        'sort': sort,
        'category': category,
        'profile_type': profile_type,
        'min_price': _decimal(request.GET.get('min_price')),
        'max_price': _decimal(request.GET.get('max_price')),
        'max_validity': _int(request.GET.get('max_validity')),
        'min_data_gb': _float(request.GET.get('min_data_gb')),
        'unlimited': request.GET.get('unlimited') == '1',
        'calls_sms': request.GET.get('calls_sms') == '1',
        'page': page,
        'page_size': PAGE_SIZE,
    }


def apply_client_filters(bundles: list[dict[str, Any]], params: dict[str, Any]) -> list[dict[str, Any]]:
    filtered = []
    min_data_mb = None
    if params.get('min_data_gb') is not None:
        min_data_mb = params['min_data_gb'] * 1024

    for bundle in bundles:
        price = bundle.get('price')
        if params.get('min_price') is not None:
            if price is None or Decimal(str(price)) < params['min_price']:
                continue
        if params.get('max_price') is not None:
            if price is None or Decimal(str(price)) > params['max_price']:
                continue

        validity = bundle.get('validity')
        if params.get('max_validity') is not None:
            if validity is None or int(validity) > params['max_validity']:
                continue

        if params.get('unlimited'):
            if not bundle.get('unlimited'):
                continue

        if params.get('calls_sms'):
            if not bundle.get('supports_calls_sms'):
                continue

        if min_data_mb is not None:
            if bundle.get('unlimited'):
                pass
            else:
                data_mb = bundle_data_mb(bundle)
                if data_mb is None or data_mb < min_data_mb:
                    continue

        filtered.append(bundle)
    return filtered


def search_esim_bundles(params: dict[str, Any]) -> dict[str, Any]:
    api_result = get_bundles(
        country_code=params['country'],
        region_code=params['region'],
        page_number=params['page'],
        page_size=params['page_size'],
        sort_by=params['sort'],
        bundle_category=params['category'],
        bundle_name=params['q'],
        profile_type=params['profile_type'],
    )
    raw_bundles = api_result.get('bundles') or []
    api_total = int(api_result.get('total') or 0)

    bundles = [enrich_bundle(dict(item)) for item in raw_bundles]
    bundles = apply_client_filters(bundles, params)

    loaded_through = params['page'] * params['page_size']
    has_more = loaded_through < api_total

    return {
        'bundles': bundles,
        'api_total': api_total,
        'has_more': has_more,
        'next_page': params['page'] + 1,
    }


def esim_search_context(request, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = params or parse_esim_search(request)
    countries = []
    regions = []
    api_error = ''
    result = {'bundles': [], 'api_total': 0, 'has_more': False, 'next_page': 2}

    try:
        countries = sorted(
            get_cached_countries(),
            key=lambda item: (item.get('country_name') or '').lower(),
        )
        regions = sorted(
            get_cached_regions(),
            key=lambda item: (item.get('region_name') or item.get('region_code') or '').lower(),
        )
        result = search_esim_bundles(params)
    except MontyESIMError as exc:
        api_error = str(exc)

    filters_active = any([
        params['country'],
        params['region'],
        params['q'],
        params['category'] != 'country',
        params['profile_type'],
        params['min_price'] is not None,
        params['max_price'] is not None,
        params['max_validity'] is not None,
        params['min_data_gb'] is not None,
        params['unlimited'],
        params['calls_sms'],
        params['sort'] != 'price_asc',
    ])

    return {
        'countries': countries,
        'regions': regions,
        'bundles': result['bundles'],
        'api_total': result['api_total'],
        'has_more': result['has_more'],
        'next_page': result['next_page'],
        'api_error': api_error,
        'search': params,
        'qparams': request.GET,
        'filters_active': filters_active,
        'sort_options': SORT_OPTIONS,
        'category_options': CATEGORY_OPTIONS,
        'profile_options': PROFILE_OPTIONS,
        'validity_options': VALIDITY_OPTIONS,
        'data_options': DATA_OPTIONS,
        'price_max_options': PRICE_MAX_OPTIONS,
    }
