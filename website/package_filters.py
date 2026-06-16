from django.utils.translation import gettext_lazy as _


PRICE_FILTER_OPTIONS = [
    ('', _('Any price')),
    ('500', _('Up to $500')),
    ('1000', _('Up to $1,000')),
    ('1500', _('Up to $1,500')),
    ('2000', _('Up to $2,000')),
    ('5000', _('Up to $5,000')),
    ('10000', _('Up to $10,000')),
]


def apply_package_filters(queryset, request):
    country = request.GET.get('country', '').strip()
    price_max = request.GET.get('price_max', '').strip()

    if country:
        queryset = queryset.filter(country=country)

    if price_max:
        from decimal import Decimal, InvalidOperation

        try:
            queryset = queryset.filter(starting_price__lte=Decimal(price_max))
        except (InvalidOperation, ValueError):
            pass

    return queryset


def get_country_choices():
    from .models import TravelPackage

    return list(
        TravelPackage.objects.filter(is_active=True)
        .values_list('country', flat=True)
        .distinct()
        .order_by('country')
    )


def package_filter_context(request):
    return {
        'country_choices': get_country_choices(),
        'price_filter_options': PRICE_FILTER_OPTIONS,
        'current_country': request.GET.get('country', ''),
        'current_price_max': request.GET.get('price_max', ''),
        'filters_active': bool(
            request.GET.get('country', '').strip()
            or request.GET.get('price_max', '').strip()
        ),
    }
