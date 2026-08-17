import io
import uuid

import qrcode
from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _

from .esim_filters import esim_search_context, parse_esim_search, search_esim_bundles
from .forms import EsimOrderLookupForm, EsimPurchaseForm
from .models import EsimOrder, TravelPackage, Destination, VisaRequirement, Testimonial
from .ims_countries import iso3_countries
from .monty_esim import (
    MontyESIMError,
    assign_bundle,
    get_cached_countries,
    get_order_activation_code,
    resend_order_email,
)
from .package_filters import apply_package_filters, package_filter_context


def _active_testimonials():
    return Testimonial.objects.filter(is_active=True)


def _filtered_packages(request, limit=None):
    qs = apply_package_filters(
        TravelPackage.objects.filter(is_active=True),
        request,
    )
    if limit and not package_filter_context(request)['filters_active']:
        return qs[:limit]
    return qs


def _new_order_reference() -> str:
    return f'SAM-{uuid.uuid4().hex[:12].upper()}'


def _grant_esim_order_access(request, order: EsimOrder) -> None:
    request.session['esim_order_id'] = order.pk


def _can_view_esim_order(request, order: EsimOrder) -> bool:
    if request.session.get('esim_order_id') == order.pk:
        return True
    return request.user.is_authenticated and request.user.is_staff


def home(request):
    esim_countries = []
    try:
        esim_countries = sorted(
            get_cached_countries(),
            key=lambda item: (item.get('country_name') or '').lower(),
        )
    except MontyESIMError:
        pass

    return render(request, 'website/home.html', {
        'packages': TravelPackage.objects.filter(is_active=True)[:6],
        'destinations': Destination.objects.filter(is_active=True)[:8],
        'testimonials': _active_testimonials(),
        'filter_action': reverse('website:packages'),
        'esim_countries': esim_countries,
        'insurance_countries': iso3_countries(),
        'default_residence': settings.SWAN_IMS_DEFAULT_RESIDENCE,
        **package_filter_context(request),
    })


def about(request):
    return render(request, 'website/about.html', {
        'testimonials': _active_testimonials(),
    })


def packages(request):
    return render(request, 'website/packages.html', {
        'packages': _filtered_packages(request),
        **package_filter_context(request),
    })


def package_detail(request, slug):
    package = get_object_or_404(
        TravelPackage.objects.prefetch_related('gallery_images'),
        slug=slug,
        is_active=True,
    )
    related = (
        TravelPackage.objects.filter(is_active=True, country=package.country)
        .exclude(pk=package.pk)[:3]
    )
    if related.count() < 2:
        related = TravelPackage.objects.filter(is_active=True).exclude(pk=package.pk)[:3]

    return render(request, 'website/package_detail.html', {
        'package': package,
        'gallery': package.gallery_items(),
        'related_packages': related,
    })


def visa_requirements(request):
    visas = (
        VisaRequirement.objects.filter(is_active=True)
        .exclude(pdf_file='')
        .exclude(pdf_file__isnull=True)
    )
    return render(request, 'website/visa.html', {
        'visa_requirements': visas,
    })


def contact(request):
    return render(request, 'website/contact.html')


def esim(request):
    params = parse_esim_search(request)
    purchase_form = EsimPurchaseForm()
    selected_bundle = None
    auto_open_buy_code = ''

    context = esim_search_context(request, params)
    buy_code = (request.GET.get('buy') or '').strip()
    bundles = context.get('bundles') or []
    if buy_code and bundles:
        for bundle in bundles:
            if bundle.get('bundle_code') == buy_code:
                selected_bundle = bundle
                auto_open_buy_code = buy_code
                break

    context.update({
        'purchase_form': purchase_form,
        'selected_bundle': selected_bundle,
        'auto_open_buy_code': auto_open_buy_code,
        'country_code': params['country'],
    })
    return render(request, 'website/esim.html', context)


def esim_load_more(request):
    params = parse_esim_search(request)
    page = int(request.GET.get('page') or params['page'] or 2)
    params['page'] = max(page, 2)

    try:
        result = search_esim_bundles(params)
    except MontyESIMError as exc:
        return JsonResponse({'error': str(exc)}, status=502)

    html = render_to_string(
        'includes/esim_bundle_cards.html',
        {'bundles': result['bundles']},
        request=request,
    )
    return JsonResponse({
        'html': html,
        'has_more': result['has_more'],
        'next_page': result['next_page'],
        'count': len(result['bundles']),
    })


def esim_purchase(request):
    if request.method != 'POST':
        return redirect('website:esim')

    form = EsimPurchaseForm(request.POST)
    if not form.is_valid():
        messages.error(request, _('Please check the form and try again.'))
        bundle_code = (request.POST.get('bundle_code') or '').strip()
        if bundle_code:
            return redirect(f"{reverse('website:esim')}?buy={bundle_code}")
        return redirect('website:esim')

    data = form.cleaned_data
    order_reference = _new_order_reference()

    try:
        assign_result = assign_bundle(
            bundle_code=data['bundle_code'],
            email=data['customer_email'],
            name=data['customer_name'],
            order_reference=order_reference,
            whatsapp_number=data.get('customer_whatsapp') or '',
        )
        monty_order_id = assign_result.get('order_id') or ''
        activation_code = ''
        order_status = ''
        if monty_order_id:
            activation_code = get_order_activation_code(monty_order_id)
            from .monty_esim import get_order
            order_detail = get_order(monty_order_id) or {}
            order_status = order_detail.get('order_status') or ''

        order = EsimOrder.objects.create(
            order_reference=order_reference,
            monty_order_id=monty_order_id,
            bundle_code=data['bundle_code'],
            bundle_name=data.get('bundle_name') or '',
            customer_name=data['customer_name'],
            customer_email=data['customer_email'],
            customer_whatsapp=data.get('customer_whatsapp') or '',
            iccid=assign_result.get('iccid') or '',
            activation_code=activation_code,
            price_usd=data.get('bundle_price'),
            order_status=order_status,
            api_message=assign_result.get('message') or '',
        )
        _grant_esim_order_access(request, order)
        return redirect('website:esim_success', pk=order.pk)

    except MontyESIMError as exc:
        messages.error(request, str(exc))
        return redirect(f"{reverse('website:esim')}?buy={data['bundle_code']}")


def esim_lookup(request):
    form = EsimOrderLookupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ref = form.cleaned_data['order_reference'].strip()
        email = form.cleaned_data['customer_email'].strip()
        order = EsimOrder.objects.filter(
            order_reference__iexact=ref,
            customer_email__iexact=email,
        ).first()
        if order:
            _grant_esim_order_access(request, order)
            return redirect('website:esim_success', pk=order.pk)
        messages.error(
            request,
            _('No order found for that email and reference. Check your details or contact us.'),
        )
    return render(request, 'website/esim_lookup.html', {'form': form})


def esim_resend_email(request, pk):
    if request.method != 'POST':
        return redirect('website:esim_success', pk=pk)

    order = get_object_or_404(EsimOrder, pk=pk)
    if not _can_view_esim_order(request, order):
        raise Http404

    if not order.monty_order_id:
        messages.error(
            request,
            _('This order cannot receive an email yet. Try again shortly or contact us.'),
        )
        return redirect('website:esim_success', pk=pk)

    try:
        result = resend_order_email(order.monty_order_id)
        msg = result.get('message') or _('Email sent successfully. Check your inbox.')
        messages.success(request, msg)
    except MontyESIMError as exc:
        messages.error(request, str(exc))

    return redirect('website:esim_success', pk=pk)


def esim_success(request, pk):
    order = get_object_or_404(EsimOrder, pk=pk)
    if not _can_view_esim_order(request, order):
        raise Http404

    if not order.activation_code and order.monty_order_id:
        try:
            activation_code = get_order_activation_code(order.monty_order_id, attempts=3, delay=1.0)
            if activation_code:
                order.activation_code = activation_code
                order.save(update_fields=['activation_code'])
        except MontyESIMError:
            pass

    return render(request, 'website/esim_success.html', {'order': order})


def esim_qr(request, pk):
    order = get_object_or_404(EsimOrder, pk=pk)
    if not _can_view_esim_order(request, order) or not order.activation_code:
        raise Http404

    image = qrcode.make(order.activation_code)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')
