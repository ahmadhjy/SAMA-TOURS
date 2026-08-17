import json
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from .ims_countries import country_name, iso3_countries
from .insurance_forms import InsuranceLookupForm, InsurancePurchaseForm, InsuranceQuoteForm
from .insurance_filters import (
    COVID_OPTIONS,
    CURRENCY_OPTIONS_BASE,
    MAX_PRICE_OPTIONS,
    SORT_OPTIONS,
    TIER_OPTIONS,
    currency_options_from_offers,
    filter_and_sort_offers,
    filters_active,
    insurance_filter_context,
    parse_insurance_filters,
)
from .insurance_plans import enrich_offer
from .models import TravelInsuranceOrder
from .swan_ims import (
    SwanIMSError,
    create_travel_contract,
    extract_contract_code,
    flatten_plan_offers,
    get_contract_pdf,
    get_travel_plans,
    send_contract_email,
)


def _insurance_reference() -> str:
    return f'SAM-INS-{uuid.uuid4().hex[:10].upper()}'


def _grant_insurance_access(request, order: TravelInsuranceOrder) -> None:
    request.session['insurance_order_id'] = order.pk


def _can_view_insurance_order(request, order: TravelInsuranceOrder) -> bool:
    if request.session.get('insurance_order_id') == order.pk:
        return True
    return request.user.is_authenticated and request.user.is_staff


def _price_ids_for_tier(offer: dict, tier: str) -> list[int]:
    price_matrix = (offer.get('raw_plan') or {}).get('price') or []
    ids = []
    for traveller_prices in price_matrix:
        if not isinstance(traveller_prices, list) or not traveller_prices:
            continue
        match = next(
            (r for r in traveller_prices if isinstance(r, dict) and r.get('Deductible') == tier),
            traveller_prices[0],
        )
        if isinstance(match, dict) and match.get('id') is not None:
            ids.append(int(match['id']))
    return ids


def _trip_days(from_date: str, till_date: str) -> int:
    start = datetime.strptime(from_date, '%Y-%m-%d').date()
    end = datetime.strptime(till_date, '%Y-%m-%d').date()
    return max((end - start).days + 1, 1)


def _fetch_insurance_quote(request) -> dict:
    if request.GET:
        quote_form = InsuranceQuoteForm(request.GET)
    else:
        quote_form = InsuranceQuoteForm(initial={
            'residence_country': settings.SWAN_IMS_DEFAULT_RESIDENCE,
            'traveller_count': 1,
        })

    offers = []
    api_error = ''
    quote_data = None

    if request.GET and quote_form.is_valid():
        quote_data = quote_form.quote_session_data()
        quote_data['destination_label'] = country_name(quote_data['destination_country'])
        quote_data['residence_label'] = country_name(quote_data['residence_country'])
        quote_data['trip_days'] = _trip_days(quote_data['from_date'], quote_data['till_date'])
        try:
            plans = get_travel_plans(
                residence_country=quote_data['residence_country'],
                destinations=quote_form.destinations_payload(),
                travellers=[{'birth_date': d} for d in quote_data['birth_dates']],
            )
            offers = [
                enrich_offer(offer, trip_days=quote_data['trip_days'])
                for offer in flatten_plan_offers(plans)
            ]
            for offer in offers:
                raw = offer.get('raw_plan') or {}
                offer['price_ids_no_deductible'] = _price_ids_for_tier(
                    {'raw_plan': raw}, '0',
                )
                offer['price_ids_with_deductible'] = _price_ids_for_tier(
                    {'raw_plan': raw}, '1',
                )
                offer['benefits_json'] = json.dumps(offer.get('benefits') or [])
        except SwanIMSError as exc:
            api_error = str(exc)

    plan_filters = parse_insurance_filters(request.GET)
    total_plans = len(offers)
    currency_options = currency_options_from_offers(offers) if offers else list(CURRENCY_OPTIONS_BASE)
    if offers:
        offers, total_plans = filter_and_sort_offers(offers, plan_filters)

    return {
        'quote_form': quote_form,
        'offers': offers,
        'total_plans': total_plans,
        'plan_filters': plan_filters,
        'filters_active': filters_active(plan_filters),
        'currency_options': currency_options,
        'quote_data': quote_data,
        'api_error': api_error,
    }


def insurance(request):
    ctx = _fetch_insurance_quote(request)
    quote_form = ctx['quote_form']
    offers = ctx['offers']
    quote_data = ctx['quote_data']
    api_error = ctx['api_error']

    purchase_form = None
    auto_open_plan_id = ''

    buy_plan = (request.GET.get('buy') or '').strip()
    if buy_plan and offers:
        for offer in offers:
            if str(offer.get('plan_id')) == buy_plan:
                auto_open_plan_id = buy_plan
                purchase_form = InsurancePurchaseForm(initial={
                    'plan_id': offer['plan_id'],
                    'plan_name': offer['name'],
                    'plan_price': offer['total_price'],
                    'plan_currency': offer['currency'],
                    'deductible_tier': offer['default_tier'],
                    'quote_data': json.dumps(quote_data),
                    'price_ids': ','.join(str(i) for i in offer['selected_price_ids']),
                })
                break

    if settings.SWAN_IMS_ALLOW_CHECKOUT:
        if not purchase_form:
            purchase_form = InsurancePurchaseForm(initial={
                'quote_data': json.dumps(quote_data) if quote_data else '',
            })

    scroll_to_results = bool(request.GET)

    return render(request, 'website/insurance.html', {
        'quote_form': quote_form,
        'offers': offers,
        'quote_data': quote_data,
        'api_error': api_error,
        'purchase_form': purchase_form,
        'auto_open_plan_id': auto_open_plan_id,
        'sandbox_mode': settings.SWAN_IMS_SANDBOX,
        'checkout_enabled': settings.SWAN_IMS_ALLOW_CHECKOUT,
        'scroll_to_results': scroll_to_results,
        **insurance_filter_context(ctx),
    })


def insurance_quote(request):
    """AJAX quote — returns HTML fragment for the results panel."""
    ctx = _fetch_insurance_quote(request)
    quote_form = ctx['quote_form']

    html = render_to_string(
        'includes/insurance_results.html',
        {
            'quote_form': quote_form,
            'offers': ctx['offers'],
            'quote_data': ctx['quote_data'],
            'api_error': ctx['api_error'],
            'checkout_enabled': settings.SWAN_IMS_ALLOW_CHECKOUT,
            'form_errors': quote_form.errors if quote_form.is_bound else None,
            **insurance_filter_context(ctx),
        },
        request=request,
    )

    return JsonResponse({
        'ok': quote_form.is_valid() and not ctx['api_error'],
        'html': html,
        'has_plans': bool(ctx['total_plans']),
        'quote_data': ctx['quote_data'],
    })


def insurance_purchase(request):
    if not settings.SWAN_IMS_ALLOW_CHECKOUT:
        messages.error(
            request,
            _('Online purchase is not available yet. Payment integration is coming soon — contact us for assistance.'),
        )
        return redirect('website:insurance')

    if request.method != 'POST':
        return redirect('website:insurance')

    form = InsurancePurchaseForm(request.POST)
    if not form.is_valid():
        for field, errors in form.errors.items():
            if field == '__all__':
                for error in errors:
                    messages.error(request, error)
            else:
                label = form.fields[field].label if field in form.fields else field
                for error in errors:
                    messages.error(
                        request,
                        _('%(field)s: %(error)s') % {'field': label, 'error': error},
                    )
        return redirect('website:insurance')

    if settings.SWAN_IMS_SANDBOX and not form.cleaned_data.get('confirm_sandbox'):
        messages.error(request, _('Please confirm sandbox test mode.'))
        return redirect('website:insurance')

    data = form.cleaned_data
    quote_data = data['quote_data']
    order_reference = _insurance_reference()

    try:
        result = create_travel_contract(
            residence_country=quote_data['residence_country'],
            plan_id=data['plan_id'],
            phone=data['phone'],
            email=data['email'],
            address=data['address'],
            destinations=[{
                'country': quote_data['destination_country'],
                'from_date': quote_data['from_date'],
                'till_date': quote_data['till_date'],
            }],
            travellers=form.travellers_payload(quote_data, data['price_ids']),
        )
        contract_code = extract_contract_code(result)
        if not contract_code:
            raise SwanIMSError(result.get('message') or _('Contract was not created.'))

        order = TravelInsuranceOrder.objects.create(
            order_reference=order_reference,
            contract_code=contract_code,
            plan_id=data['plan_id'],
            plan_name=data['plan_name'],
            total_price=data['plan_price'],
            currency=data['plan_currency'],
            residence_country=quote_data['residence_country'],
            destination_country=quote_data['destination_country'],
            from_date=datetime.strptime(quote_data['from_date'], '%Y-%m-%d').date(),
            till_date=datetime.strptime(quote_data['till_date'], '%Y-%m-%d').date(),
            customer_email=data['email'],
            customer_phone=data['phone'],
            customer_address=data['address'],
            travellers_json=form.travellers_payload(quote_data, data['price_ids']),
            api_message=result.get('message') or '',
        )
        _grant_insurance_access(request, order)
        return redirect('website:insurance_success', pk=order.pk)

    except SwanIMSError as exc:
        messages.error(request, str(exc))
        return redirect('website:insurance')


def insurance_success(request, pk):
    order = get_object_or_404(TravelInsuranceOrder, pk=pk)
    if not _can_view_insurance_order(request, order):
        raise Http404
    return render(request, 'website/insurance_success.html', {
        'order': order,
        'destination_label': country_name(order.destination_country),
        'sandbox_mode': settings.SWAN_IMS_SANDBOX,
    })


def insurance_pdf(request, pk):
    order = get_object_or_404(TravelInsuranceOrder, pk=pk)
    if not _can_view_insurance_order(request, order) or not order.contract_code:
        raise Http404
    try:
        pdf_bytes = get_contract_pdf(order.contract_code)
    except SwanIMSError as exc:
        raise Http404 from exc
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{order.contract_code}.pdf"'
    return response


def insurance_resend_email(request, pk):
    if request.method != 'POST':
        return redirect('website:insurance_success', pk=pk)

    order = get_object_or_404(TravelInsuranceOrder, pk=pk)
    if not _can_view_insurance_order(request, order) or not order.contract_code:
        raise Http404

    try:
        result = send_contract_email(order.contract_code, order.customer_email)
        msg = result.get('message') or _('Policy documents sent. Check your inbox.')
        messages.success(request, msg)
    except SwanIMSError as exc:
        messages.error(request, str(exc))

    return redirect('website:insurance_success', pk=pk)


def insurance_lookup(request):
    form = InsuranceLookupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ref = form.cleaned_data['order_reference'].strip()
        email = form.cleaned_data['customer_email'].strip()
        order = TravelInsuranceOrder.objects.filter(
            order_reference__iexact=ref,
            customer_email__iexact=email,
        ).first()
        if order:
            _grant_insurance_access(request, order)
            return redirect('website:insurance_success', pk=order.pk)
        messages.error(
            request,
            _('No policy found for that email and reference. Check your details or contact us.'),
        )
    return render(request, 'website/insurance_lookup.html', {'form': form})
