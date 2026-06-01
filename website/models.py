from decimal import Decimal
from django.db import models
from urllib.parse import quote


def package_image_path(instance, filename):
    safe_name = instance.name.replace(' ', '_')[:40]
    return f'package_images/{safe_name}_{filename}'


class TravelPackage(models.Model):
    name = models.CharField(max_length=200, help_text='Package title shown on the website')
    destination = models.CharField(max_length=120, help_text='Location, e.g. Dubai, UAE')
    duration = models.CharField(max_length=80, help_text='e.g. 7 Days / 6 Nights')
    starting_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Starting price in USD (used for display and filtering)',
    )
    short_description = models.TextField(help_text='Short description on the package card')
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

    @property
    def image_url(self):
        if self.featured_image:
            return self.featured_image.url
        return self.featured_image_url or ''

    @property
    def price_display(self):
        amount = self.starting_price
        if amount == amount.to_integral_value():
            return f'From ${int(amount):,}'
        return f'From ${amount:,.2f}'

    def whatsapp_booking_url(self):
        message = f"Hello, I'm interested in the package: {self.name}"
        return f'https://wa.me/96176832813?text={quote(message)}'


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
