from django.shortcuts import get_object_or_404, render
from django.urls import reverse

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
    return render(request, 'website/home.html', {
        'packages': TravelPackage.objects.filter(is_active=True)[:6],
        'destinations': Destination.objects.filter(is_active=True)[:8],
        'testimonials': _active_testimonials(),
        'filter_action': reverse('website:packages'),
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
    package = get_object_or_404(TravelPackage, slug=slug, is_active=True)
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
