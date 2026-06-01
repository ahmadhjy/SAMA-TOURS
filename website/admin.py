from django.contrib import admin
from django.utils.html import format_html

from .models import TravelPackage, Destination, VisaRequirement, Testimonial


@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'destination', 'starting_price', 'image_preview',
        'is_featured', 'is_active', 'display_order',
    )
    list_filter = ('is_featured', 'is_active', 'destination')
    search_fields = ('name', 'destination')
    list_editable = ('is_featured', 'is_active', 'display_order')
    ordering = ('display_order', 'name')
    fieldsets = (
        ('Package details', {
            'fields': ('name', 'destination', 'duration', 'starting_price', 'short_description'),
            'description': 'Fill in the basics. Book Now on the website opens WhatsApp automatically.',
        }),
        ('Image', {
            'fields': ('featured_image', 'featured_image_url'),
            'description': 'Upload the main image, or paste an image URL.',
        }),
        ('Visibility', {
            'fields': ('is_featured', 'is_active', 'display_order'),
        }),
    )

    @admin.display(description='Image')
    def image_preview(self, obj):
        url = obj.image_url
        if url:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', url)
        return '—'


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('name', 'country')


@admin.register(VisaRequirement)
class VisaRequirementAdmin(admin.ModelAdmin):
    list_display = ('country_name', 'has_pdf_display', 'has_image_display', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('country_name',)
    ordering = ('display_order', 'country_name')
    fieldsets = (
        (None, {
            'fields': ('country_name', 'display_order', 'is_active'),
        }),
        ('Card display', {
            'fields': ('featured_image', 'featured_image_url'),
            'description': 'Upload an image for the card, or paste an image URL.',
        }),
        ('PDF document', {
            'fields': ('pdf_file',),
            'description': 'Upload the visa requirements PDF. Visitors click the card to open this file.',
        }),
    )

    @admin.display(boolean=True, description='PDF')
    def has_pdf_display(self, obj):
        return obj.has_pdf

    @admin.display(boolean=True, description='Image')
    def has_image_display(self, obj):
        return bool(obj.featured_image or obj.featured_image_url)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('author_name', 'content')
