from decimal import Decimal, InvalidOperation

from django.db.models import QuerySet


PRICE_FILTER_OPTIONS = [
    ('', 'Any price'),
    ('500', 'Up to $500'),
    ('1000', 'Up to $1,000'),
    ('1500', 'Up to $1,500'),
    ('2000', 'Up to $2,000'),
    ('5000', 'Up to $5,000'),
]


def apply_package_filters(queryset: QuerySet, request) -> QuerySet:
    destination = request.GET.get('destination', '').strip()
    price_max = request.GET.get('price_max', '').strip()

    if destination:
        queryset = queryset.filter(destination__icontains=destination)

    if price_max:
        try:
            queryset = queryset.filter(starting_price__lte=Decimal(price_max))
        except (InvalidOperation, ValueError):
            pass

    return queryset


def get_destination_choices():
    from .models import TravelPackage

    return list(
        TravelPackage.objects.filter(is_active=True)
        .values_list('destination', flat=True)
        .distinct()
        .order_by('destination')
    )


def package_filter_context(request):
    return {
        'destination_choices': get_destination_choices(),
        'price_filter_options': PRICE_FILTER_OPTIONS,
        'current_destination': request.GET.get('destination', ''),
        'current_price_max': request.GET.get('price_max', ''),
        'filters_active': bool(
            request.GET.get('destination', '').strip()
            or request.GET.get('price_max', '').strip()
        ),
    }
