from modeltranslation.translator import TranslationOptions, translator

from .models import Destination, Testimonial, TravelPackage, VisaRequirement


class TravelPackageTranslationOptions(TranslationOptions):
    fields = (
        'name',
        'duration',
        'short_description',
        'full_description',
        'itinerary',
        'highlights',
    )


class VisaRequirementTranslationOptions(TranslationOptions):
    fields = ('country_name',)


class TestimonialTranslationOptions(TranslationOptions):
    fields = ('content',)


class DestinationTranslationOptions(TranslationOptions):
    fields = ('description',)


translator.register(TravelPackage, TravelPackageTranslationOptions)
translator.register(VisaRequirement, VisaRequirementTranslationOptions)
translator.register(Testimonial, TestimonialTranslationOptions)
translator.register(Destination, DestinationTranslationOptions)
