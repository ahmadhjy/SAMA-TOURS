"""Monty eSIM Reseller API client."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY = 'monty_esim_session'
AUTH_STYLES = ('access_token', 'bearer')


class MontyESIMError(Exception):
    """API or configuration error."""


@dataclass
class MontySession:
    access_token: str
    refresh_token: str
    reseller_id: str
    expires_at: float

    @classmethod
    def from_login(cls, payload: dict[str, Any]) -> MontySession:
        expires_in = int(payload.get('expires_in') or 300)
        return cls(
            access_token=payload['access_token'],
            refresh_token=payload.get('refresh_token', ''),
            reseller_id=payload.get('reseller_id', ''),
            expires_at=time.time() + max(expires_in - 30, 60),
        )


def _base_url() -> str:
    return settings.MONTY_ESIM_API_BASE_URL.rstrip('/')


def _credentials_configured() -> bool:
    return bool(settings.MONTY_ESIM_USERNAME and settings.MONTY_ESIM_PASSWORD)


def _parse_json(raw: bytes) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise MontyESIMError('Invalid JSON response from Monty API.') from exc


def _http_request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    auth_style: str = 'access_token',
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f'{_base_url()}{path}'
    if params:
        clean = {k: v for k, v in params.items() if v is not None and v != ''}
        if clean:
            url = f'{url}?{urlencode(clean)}'

    headers = {'Accept': 'application/json'}
    payload = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        payload = json.dumps(body).encode('utf-8')

    if token:
        if auth_style == 'bearer':
            headers['Authorization'] = f'Bearer {token}'
        else:
            headers['Access-Token'] = token

    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return _parse_json(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        raise MontyESIMError(f'Monty API HTTP {exc.code}: {detail[:500]}') from exc
    except urllib.error.URLError as exc:
        raise MontyESIMError(f'Monty API connection failed: {exc.reason}') from exc


def _request_with_auth(
    method: str,
    path: str,
    *,
    session: MontySession,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    last_error: MontyESIMError | None = None
    for auth_style in AUTH_STYLES:
        try:
            return _http_request(
                method,
                path,
                token=session.access_token,
                auth_style=auth_style,
                params=params,
                body=body,
            )
        except MontyESIMError as exc:
            if 'HTTP 401' in str(exc) or 'HTTP 403' in str(exc):
                last_error = exc
                continue
            raise
    if last_error:
        raise last_error
    raise MontyESIMError('Monty API authentication failed.')


def login() -> MontySession:
    if not _credentials_configured():
        raise MontyESIMError('Monty eSIM credentials are not configured.')

    payload = _http_request(
        'POST',
        '/Agent/login',
        body={
            'username': settings.MONTY_ESIM_USERNAME,
            'password': settings.MONTY_ESIM_PASSWORD,
        },
    )
    if not payload.get('access_token'):
        message = payload.get('message') or payload.get('developer_message') or 'Login failed.'
        raise MontyESIMError(message)
    session = MontySession.from_login(payload)
    cache.set(
        CACHE_KEY,
        {
            'access_token': session.access_token,
            'refresh_token': session.refresh_token,
            'reseller_id': session.reseller_id,
            'expires_at': session.expires_at,
        },
        timeout=max(int(session.expires_at - time.time()), 60),
    )
    return session


def refresh_session(session: MontySession) -> MontySession:
    if not session.refresh_token:
        return login()
    payload = _http_request(
        'POST',
        '/Token/Refresh',
        body={'refresh_token': session.refresh_token},
    )
    if payload.get('access_token'):
        return MontySession.from_login(payload)
    return login()


def get_session() -> MontySession:
    cached = cache.get(CACHE_KEY)
    if cached and cached.get('expires_at', 0) > time.time():
        return MontySession(
            access_token=cached['access_token'],
            refresh_token=cached.get('refresh_token', ''),
            reseller_id=cached.get('reseller_id', ''),
            expires_at=cached['expires_at'],
        )
    return login()


def get_countries() -> list[dict[str, Any]]:
    session = get_session()
    payload = _request_with_auth(
        'GET',
        '/AvailableCountries',
        session=session,
        params={'reseller_id': session.reseller_id},
    )
    return payload.get('countries') or []


def get_cached_countries() -> list[dict[str, Any]]:
    cached = cache.get('monty_esim_countries')
    if cached is not None:
        return cached
    countries = get_countries()
    cache.set('monty_esim_countries', countries, timeout=3600)
    return countries


def get_regions() -> list[dict[str, Any]]:
    session = get_session()
    payload = _request_with_auth(
        'GET',
        '/AvailableRegions',
        session=session,
        params={'reseller_id': session.reseller_id},
    )
    return payload.get('regions') or []


def get_cached_regions() -> list[dict[str, Any]]:
    cached = cache.get('monty_esim_regions')
    if cached is not None:
        return cached
    regions = get_regions()
    cache.set('monty_esim_regions', regions, timeout=3600)
    return regions


def get_bundles(
    *,
    country_code: str = '',
    page_number: int = 1,
    page_size: int = 50,
    sort_by: str = '',
    bundle_category: str = 'country',
    bundle_name: str = '',
    region_code: str = '',
    profile_type: str = '',
) -> dict[str, Any]:
    session = get_session()
    params: dict[str, Any] = {
        'reseller_id': session.reseller_id,
        'page_number': page_number,
        'page_size': page_size,
        'currency_code': settings.MONTY_ESIM_CURRENCY,
    }
    if bundle_category:
        params['bundle_category'] = bundle_category
    if country_code:
        params['country_code'] = country_code
    if region_code:
        params['region_code'] = region_code
    if sort_by:
        params['sort_by'] = sort_by
    if bundle_name:
        params['bundle_name'] = bundle_name
    if profile_type:
        params['profile_type'] = profile_type

    payload = _request_with_auth('GET', '/Bundles', session=session, params=params)
    return {
        'bundles': payload.get('bundles') or [],
        'total': payload.get('total_bundles_count') or 0,
    }


def assign_bundle(
    *,
    bundle_code: str,
    email: str,
    name: str,
    order_reference: str,
    whatsapp_number: str = '',
) -> dict[str, Any]:
    session = get_session()
    body: dict[str, Any] = {
        'bundle_code': bundle_code,
        'email': email,
        'name': name,
        'order_reference': order_reference,
    }
    if whatsapp_number:
        body['whatsapp_number'] = whatsapp_number

    return _request_with_auth(
        'POST',
        '/Bundles',
        session=session,
        params={
            'reseller_id': session.reseller_id,
            'currency_code': settings.MONTY_ESIM_CURRENCY,
        },
        body=body,
    )


def get_order(order_id: str) -> dict[str, Any] | None:
    session = get_session()
    payload = _request_with_auth(
        'GET',
        '/Orders',
        session=session,
        params={
            'reseller_id': session.reseller_id,
            'order_id': order_id,
            'page_size': 1,
            'page_number': 1,
        },
    )
    orders = payload.get('orders') or []
    for item in orders:
        if isinstance(item, dict) and item.get('order_id') == order_id:
            return item
    return orders[0] if orders and isinstance(orders[0], dict) else None


def get_order_activation_code(order_id: str, *, attempts: int = 6, delay: float = 1.5) -> str:
    """Poll order history until activation_code is available."""
    activation_code = ''
    for attempt in range(attempts):
        order = get_order(order_id)
        if order:
            activation_code = (order.get('activation_code') or '').strip()
            if activation_code:
                return activation_code
        if attempt < attempts - 1:
            time.sleep(delay)
    return activation_code


def resend_order_email(order_id: str) -> dict[str, Any]:
    """Ask Monty to resend invoice / QR email to the customer."""
    session = get_session()
    return _request_with_auth(
        'POST',
        '/Orders/ResendEmail',
        session=session,
        params={'reseller_id': session.reseller_id},
        body={'order_id': order_id},
    )


def bundle_display_name(bundle: dict[str, Any]) -> str:
    return (
        bundle.get('bundle_marketing_name')
        or bundle.get('bundle_name')
        or bundle.get('bundle_code')
        or 'eSIM plan'
    )


def bundle_country_label(bundle: dict[str, Any]) -> str:
    names = bundle.get('country_name') or []
    if isinstance(names, list) and names:
        return names[0]
    codes = bundle.get('country_code') or []
    if isinstance(codes, list) and codes:
        return codes[0]
    return ''


def bundle_data_label(bundle: dict[str, Any]) -> str:
    if bundle.get('unlimited'):
        return 'Unlimited data'
    amount = bundle.get('gprs_limit')
    unit = bundle.get('data_unit') or 'MB'
    if amount is None:
        return ''
    return f'{amount} {unit}'


def bundle_price(bundle: dict[str, Any]) -> float | None:
    for key in ('reseller_retail_price', 'bundle_price_final', 'subscriber_price'):
        value = bundle.get(key)
        if value is not None:
            return float(value)
    return None


def bundle_data_mb(bundle: dict[str, Any]) -> float | None:
    if bundle.get('unlimited'):
        return None
    amount = bundle.get('gprs_limit')
    if amount is None:
        return None
    unit = (bundle.get('data_unit') or 'MB').upper()
    amount = float(amount)
    if unit == 'GB':
        return amount * 1024
    if unit == 'TB':
        return amount * 1024 * 1024
    return amount


def enrich_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    bundle['display_name'] = bundle_display_name(bundle)
    bundle['country_label'] = bundle_country_label(bundle)
    bundle['data_label'] = bundle_data_label(bundle)
    bundle['price'] = bundle_price(bundle)
    return bundle
