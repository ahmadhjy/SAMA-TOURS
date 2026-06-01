from django.shortcuts import render

from .models import TravelPackage, Destination, VisaRequirement, Testimonial
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


def home(request):
    filter_ctx = package_filter_context(request)
    packages = _filtered_packages(request, limit=6 if not filter_ctx['filters_active'] else None)

    return render(request, 'website/home.html', {
        'packages': packages,
        'destinations': Destination.objects.filter(is_active=True)[:8],
        'testimonials': _active_testimonials(),
        **filter_ctx,
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
