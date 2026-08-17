from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin

from .models import (
    TravelPackage, PackageImage, Destination, VisaRequirement, Testimonial,
    EsimOrder, TravelInsuranceOrder,
)


class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 2
    fields = ('image_preview', 'image', 'external_image_url', 'caption', 'display_order')
    readonly_fields = ('image_preview',)
    ordering = ('display_order',)

    @admin.display(description='Preview')
    def image_preview(self, obj):
        url = obj.image_url if obj.pk else ''
        if url:
            return format_html(
                '<img src="{}" alt="" style="height:56px;width:80px;object-fit:cover;border-radius:6px;" />',
                url,
            )
        return '—'


@admin.register(TravelPackage)
class TravelPackageAdmin(TabbedTranslationAdmin):
    list_display = (
        'name', 'country', 'city', 'starting_price', 'availability_display',
        'image_preview', 'gallery_count', 'is_featured', 'is_active', 'display_order',
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
        ('Availability', {
            'fields': ('available_from', 'available_to'),
            'description': 'Date range shown on the package page. Leave blank if always available.',
        }),
        ('Detail page content', {
            'fields': ('full_description', 'highlights', 'itinerary', 'included', 'excluded'),
            'description': (
                'Use one item per line for highlights, itinerary, included, and excluded. '
                'Itinerary example: "Day 1: Arrival and hotel check-in". '
                'Switch language tabs above to fill English, Arabic, and French.'
            ),
        }),
        ('Main image', {
            'fields': ('featured_image', 'featured_image_url'),
            'description': 'Main photo on cards and the package banner. Extra photos go in Package images below — they are not mixed with this image.',
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

    @admin.display(description='Gallery')
    def gallery_count(self, obj):
        return obj.gallery_images.count()

    @admin.display(description='Available')
    def availability_display(self, obj):
        if obj.available_from and obj.available_to:
            return f'{obj.available_from:%d %b %Y} – {obj.available_to:%d %b %Y}'
        if obj.available_from:
            return f'From {obj.available_from:%d %b %Y}'
        if obj.available_to:
            return f'Until {obj.available_to:%d %b %Y}'
        return '—'


@admin.register(Destination)
class DestinationAdmin(TabbedTranslationAdmin):
    list_display = ('name', 'country', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('name', 'country')


@admin.register(VisaRequirement)
class VisaRequirementAdmin(TabbedTranslationAdmin):
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
class TestimonialAdmin(TabbedTranslationAdmin):
    list_display = ('author_name', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('author_name', 'content')


@admin.register(EsimOrder)
class EsimOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_reference', 'customer_name', 'customer_email', 'bundle_name',
        'price_usd', 'order_status', 'has_qr_display', 'created_at',
    )
    list_filter = ('order_status', 'created_at')
    search_fields = (
        'order_reference', 'monty_order_id', 'customer_email',
        'customer_name', 'bundle_code',
    )
    readonly_fields = (
        'order_reference', 'monty_order_id', 'bundle_code', 'bundle_name',
        'customer_name', 'customer_email', 'customer_whatsapp', 'iccid',
        'activation_code', 'price_usd', 'order_status', 'api_message', 'created_at',
    )

    @admin.display(boolean=True, description='QR')
    def has_qr_display(self, obj):
        return obj.has_qr


@admin.register(TravelInsuranceOrder)
class TravelInsuranceOrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_reference', 'contract_code', 'customer_email', 'plan_name',
        'total_price', 'currency', 'destination_country', 'created_at',
    )
    list_filter = ('currency', 'created_at', 'destination_country')
    search_fields = (
        'order_reference', 'contract_code', 'customer_email', 'plan_name',
    )
    readonly_fields = (
        'order_reference', 'contract_code', 'plan_id', 'plan_name',
        'total_price', 'currency', 'residence_country', 'destination_country',
        'from_date', 'till_date', 'customer_email', 'customer_phone',
        'customer_address', 'travellers_json', 'api_message', 'created_at',
    )
