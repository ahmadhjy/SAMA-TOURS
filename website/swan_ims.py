"""Swan / Cygnet IMS v5 — travel insurance API client."""

from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY = 'swan_ims_session'


class SwanIMSError(Exception):
    """API or configuration error."""


@dataclass
class SwanSession:
    access_token: str
    tenant_id: str
    agency_id: int
    expires_at: float

    @classmethod
    def from_login(cls, payload: dict[str, Any]) -> SwanSession:
        access = (payload.get('user') or {}).get('access') or []
        first = access[0] if access else {}
        expires_at = time.time() + 3600
        expires_raw = payload.get('expires_at')
        if expires_raw:
            try:
                from datetime import datetime

                expires_at = datetime.strptime(expires_raw, '%Y-%m-%d %H:%M:%S').timestamp()
            except ValueError:
                pass
        return cls(
            access_token=payload['access_token'],
            tenant_id=str(first.get('id', '')),
            agency_id=int(first.get('agency') or 0),
            expires_at=expires_at - 60,
        )


def _base_url() -> str:
    return settings.SWAN_IMS_API_BASE_URL.rstrip('/') + '/'


def _credentials_configured() -> bool:
    return bool(settings.SWAN_IMS_USERNAME and settings.SWAN_IMS_PASSWORD)


def _parse_json(raw: bytes) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        return json.loads(raw.decode('utf-8'))
    except json.JSONDecodeError as exc:
        raise SwanIMSError('Invalid JSON response from Swan IMS API.') from exc


def _http_request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    tenant_id: str | None = None,
    body: dict[str, Any] | None = None,
    raw_response: bool = False,
) -> dict[str, Any] | bytes:
    url = _base_url() + path.lstrip('/')
    headers = {'Accept': 'application/json'}
    payload = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        payload = json.dumps(body).encode('utf-8')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if tenant_id:
        headers['Tenant'] = tenant_id

    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            if raw_response:
                return raw
            return _parse_json(raw)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        raise SwanIMSError(f'Swan IMS HTTP {exc.code}: {detail[:500]}') from exc
    except urllib.error.URLError as exc:
        raise SwanIMSError(f'Swan IMS connection failed: {exc.reason}') from exc


def login() -> SwanSession:
    if not _credentials_configured():
        raise SwanIMSError('Swan IMS credentials are not configured.')

    payload = _http_request(
        'POST',
        'api/v5/login',
        body={
            'username': settings.SWAN_IMS_USERNAME,
            'password': settings.SWAN_IMS_PASSWORD,
        },
    )
    if not payload.get('access_token'):
        message = payload.get('message') or 'Login failed.'
        raise SwanIMSError(message)

    session = SwanSession.from_login(payload)
    cache.set(
        CACHE_KEY,
        {
            'access_token': session.access_token,
            'tenant_id': session.tenant_id,
            'agency_id': session.agency_id,
            'expires_at': session.expires_at,
        },
        timeout=max(int(session.expires_at - time.time()), 60),
    )
    return session


def get_session() -> SwanSession:
    cached = cache.get(CACHE_KEY)
    if cached and cached.get('expires_at', 0) > time.time():
        return SwanSession(
            access_token=cached['access_token'],
            tenant_id=cached['tenant_id'],
            agency_id=int(cached['agency_id']),
            expires_at=cached['expires_at'],
        )
    return login()


def _authed(method: str, path: str, *, body: dict[str, Any] | None = None, raw: bool = False):
    session = get_session()
    return _http_request(
        method,
        path,
        token=session.access_token,
        tenant_id=session.tenant_id,
        body=body,
        raw_response=raw,
    )


def get_masters() -> dict[str, Any]:
    return _authed('GET', 'api/v5/general/masters')


def get_travel_plans(
    *,
    residence_country: str,
    destinations: list[dict[str, str]],
    travellers: list[dict[str, str]],
) -> list[dict[str, Any]]:
    session = get_session()
    payload = _authed(
        'POST',
        'api/v5/travel/plans',
        body={
            'country': residence_country,
            'agency': session.agency_id,
            'destinations': destinations,
            'travellers': travellers,
        },
    )
    if not payload.get('status'):
        message = payload.get('message') or 'Could not fetch insurance plans.'
        raise SwanIMSError(message)
    return payload.get('plans') or []


def create_travel_contract(
    *,
    residence_country: str,
    plan_id: int,
    phone: str,
    email: str,
    address: str,
    destinations: list[dict[str, str]],
    travellers: list[dict[str, Any]],
) -> dict[str, Any]:
    session = get_session()
    payload = _authed(
        'POST',
        'api/v5/travel/contract',
        body={
            'country': residence_country,
            'agency': session.agency_id,
            'plan_id': plan_id,
            'phone': phone,
            'email': email,
            'address': address,
            'destinations': destinations,
            'travellers': travellers,
        },
    )
    return payload


def get_contract_pdf(contract_code: str) -> bytes:
    result = _authed(
        'GET',
        f'api/v5/travel/contract/pdf?code={contract_code}',
        raw=True,
    )
    if isinstance(result, bytes):
        return result
    raise SwanIMSError('Unexpected PDF response from Swan IMS.')


def send_contract_email(contract_code: str, email: str) -> dict[str, Any]:
    return _authed(
        'POST',
        'api/v5/travel/contract/email',
        body={
            'code': contract_code,
            'email': email,
            'attachments': ['contract', 'receipt', 'general_conditions'],
        },
    )


def extract_contract_code(payload: dict[str, Any]) -> str:
    contract = payload.get('contract') or {}
    return (
        contract.get('contract_code')
        or payload.get('contract_id')
        or payload.get('contract_code')
        or ''
    )


def flatten_plan_offers(plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turn API plans into display rows with price options per deductible tier."""

    def tier_total(price_matrix: list, tier: str) -> tuple[float, list[int]]:
        total = 0.0
        price_ids: list[int] = []
        for traveller_prices in price_matrix:
            if not isinstance(traveller_prices, list) or not traveller_prices:
                continue
            match = next(
                (r for r in traveller_prices if isinstance(r, dict) and r.get('Deductible') == tier),
                traveller_prices[0],
            )
            if isinstance(match, dict):
                total += float(match.get('Price') or 0)
                if match.get('id') is not None:
                    price_ids.append(int(match['id']))
        return total, price_ids

    offers = []
    for plan in plans:
        price_matrix = plan.get('price') or []
        if not price_matrix:
            continue

        options = []
        for traveller_index, traveller_prices in enumerate(price_matrix):
            if not isinstance(traveller_prices, list):
                continue
            for price_row in traveller_prices:
                if not isinstance(price_row, dict):
                    continue
                options.append({
                    'traveller_index': traveller_index,
                    'price_id': price_row.get('id'),
                    'price': price_row.get('Price'),
                    'deductible': price_row.get('Deductible') == '1',
                    'deductible_amount': price_row.get('DeductiblePrice'),
                    'code': (price_row.get('Code') or '').strip(),
                    'days': price_row.get('ConsecutiveDays'),
                })

        total_no_ded, ids_no_ded = tier_total(price_matrix, '0')
        total_with_ded, ids_with_ded = tier_total(price_matrix, '1')
        if total_no_ded > 0:
            default_tier, total_price, selected_ids = '0', total_no_ded, ids_no_ded
        else:
            default_tier, total_price, selected_ids = '1', total_with_ded, ids_with_ded

        offers.append({
            'plan_id': plan.get('id'),
            'name': plan.get('print_name') or plan.get('name') or '',
            'full_name': plan.get('name') or '',
            'currency': plan.get('currency_code') or 'USD',
            'total_price': total_price,
            'total_with_deductible': total_with_ded if total_with_ded != total_no_ded else None,
            'total_without_deductible': total_no_ded if total_with_ded != total_no_ded else None,
            'default_tier': default_tier,
            'price_options': options,
            'selected_price_ids': selected_ids,
            'raw_plan': plan,
        })
    return sorted(offers, key=lambda item: item.get('total_price') or 0)
