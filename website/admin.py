from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin

from .models import TravelPackage, PackageImage, Destination, VisaRequirement, Testimonial


class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 1
    fields = ('image', 'external_image_url', 'caption', 'display_order')
    ordering = ('display_order',)


@admin.register(TravelPackage)
class TravelPackageAdmin(TranslationAdmin):
    list_display = (
        'name', 'country', 'city', 'starting_price', 'image_preview',
        'is_featured', 'is_active', 'display_order',
    )
    list_filter = ('is_featured', 'is_active', 'country')
    search_fields = ('name', 'country', 'city', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'is_active', 'display_order')
    ordering = ('display_order', 'name')
    inlines = [PackageImageInline]
    fieldsets = (
        ('Package details', {
            'fields': (
                'name', 'slug', 'country', 'city', 'duration', 'starting_price',
                'short_description',
            ),
        }),
        ('Detail page content', {
            'fields': ('full_description', 'highlights', 'itinerary'),
            'description': (
                'Highlights and itinerary: one item per line. '
                'Itinerary example: "Day 1: Arrival and hotel check-in".'
            ),
        }),
        ('Main image', {
            'fields': ('featured_image', 'featured_image_url'),
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
class DestinationAdmin(TranslationAdmin):
    list_display = ('name', 'country', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('name', 'country')


@admin.register(VisaRequirement)
class VisaRequirementAdmin(TranslationAdmin):
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
class TestimonialAdmin(TranslationAdmin):
    list_display = ('author_name', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('author_name', 'content')
