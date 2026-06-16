from decimal import Decimal
import re

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .countries import COUNTRY_CHOICES
from .whatsapp import package_booking_message, whatsapp_url


def package_image_path(instance, filename):
    safe_name = instance.name.replace(' ', '_')[:40]
    return f'package_images/{safe_name}_{filename}'


def package_gallery_path(instance, filename):
    pkg = instance.package.name.replace(' ', '_')[:30]
    return f'package_gallery/{pkg}_{filename}'


class TravelPackage(models.Model):
    name = models.CharField(max_length=200, help_text='Package title shown on the website')
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    country = models.CharField(
        max_length=120,
        choices=COUNTRY_CHOICES,
        help_text='Destination country',
    )
    city = models.CharField(
        max_length=120,
        blank=True,
        help_text='City or region (e.g. Dubai)',
    )
    duration = models.CharField(max_length=80, help_text='e.g. 7 Days / 6 Nights')
    starting_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Starting price in USD (used for display and filtering)',
    )
    short_description = models.TextField(help_text='Short description on the package card')
    full_description = models.TextField(
        blank=True,
        help_text='Full description on the package detail page',
    )
    itinerary = models.TextField(
        blank=True,
        help_text='One day per line, e.g. "Day 1: Arrival and hotel check-in"',
    )
    highlights = models.TextField(
        blank=True,
        help_text='One highlight per line (shown on detail page)',
    )
    featured_image = models.ImageField(
        upload_to=package_image_path,
        blank=True,
        null=True,
        help_text='Main package image',
    )
    featured_image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='Optional: image URL if you are not uploading a file',
    )
    is_featured = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            source_name = getattr(self, 'name_en', None) or self.name
            base = slugify(source_name) or 'package'
            slug = base
            counter = 1
            while TravelPackage.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def destination_display(self):
        if self.city:
            return f'{self.city}, {self.country}'
        return self.country

    @property
    def image_url(self):
        if self.featured_image:
            return self.featured_image.url
        return self.featured_image_url or ''

    @property
    def price_display(self):
        amount = self.starting_price
        if amount == amount.to_integral_value():
            return _('From $%(amount)s') % {'amount': f'{int(amount):,}'}
        return _('From $%(amount)s') % {'amount': f'{amount:,.2f}'}

    def itinerary_lines(self):
        return [line.strip() for line in self.itinerary.splitlines() if line.strip()]

    def display_itinerary_lines(self):
        """Return admin itinerary or sensible day-by-day defaults from duration."""
        lines = self.itinerary_lines()
        if lines:
            return lines

        match = re.search(r'(\d+)\s*Days?', self.duration or '', re.IGNORECASE)
        day_count = int(match.group(1)) if match else 5
        day_count = max(1, min(day_count, 14))

        templates = [
            'Arrival, airport transfer & hotel check-in',
            'Guided city tour & iconic landmarks',
            'Free day for shopping or optional excursions',
            'Cultural experiences & local cuisine',
            'Scenic day trip outside the city',
            'Leisure day — beach, spa or relaxation',
            'Adventure activity or nature excursion',
            'Departure & transfer to the airport',
        ]

        result = []
        for i in range(day_count):
            if i == 0:
                text = templates[0]
            elif i == day_count - 1 and day_count > 1:
                text = templates[-1]
            else:
                text = templates[min(i, len(templates) - 2)]
            result.append(f'Day {i + 1}: {text}')
        return result

    def highlight_lines(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]

    def gallery_items(self):
        items = []
        for img in self.gallery_images.all():
            url = img.image_url
            if url:
                items.append({'url': url, 'caption': img.caption})
        if not items and self.image_url:
            items.append({'url': self.image_url, 'caption': self.name})
        return items

    def whatsapp_booking_url(self):
        message = package_booking_message(
            self.name, self.destination_display, self.duration, self.price_display,
        )
        return whatsapp_url(message)


class PackageImage(models.Model):
    package = models.ForeignKey(
        TravelPackage,
        on_delete=models.CASCADE,
        related_name='gallery_images',
    )
    image = models.ImageField(upload_to=package_gallery_path, blank=True, null=True)
    external_image_url = models.URLField(max_length=500, blank=True)
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.caption or f'Image for {self.package.name}'

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return self.external_image_url or ''


class Destination(models.Model):
    name = models.CharField(max_length=120)
    country = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    featured_image = models.URLField(max_length=500)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f'{self.name}, {self.country}'


def visa_image_path(instance, filename):
    return f'visa_images/{instance.country_name}_{filename}'


def visa_pdf_path(instance, filename):
    return f'visa_pdfs/{instance.country_name}_{filename}'


class VisaRequirement(models.Model):
    country_name = models.CharField(max_length=120)
    featured_image = models.ImageField(
        upload_to=visa_image_path,
        blank=True,
        null=True,
        help_text='Image shown on the visa card',
    )
    featured_image_url = models.URLField(
        max_length=500,
        blank=True,
        help_text='Optional: use a URL if you are not uploading an image file',
    )
    pdf_file = models.FileField(
        upload_to=visa_pdf_path,
        blank=True,
        null=True,
        help_text='PDF opened when visitors click the card',
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'country_name']
        verbose_name_plural = 'Visa requirements'

    def __str__(self):
        return self.country_name

    @property
    def image_url(self):
        if self.featured_image:
            return self.featured_image.url
        return self.featured_image_url or ''

    @property
    def pdf_url(self):
        if self.pdf_file:
            return self.pdf_file.url
        return ''

    @property
    def has_pdf(self):
        return bool(self.pdf_file)


class Testimonial(models.Model):
    author_name = models.CharField(max_length=120)
    content = models.TextField()
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'author_name']

    def __str__(self):
        return self.author_name
