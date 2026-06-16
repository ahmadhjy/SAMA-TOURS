# Data migration — copy English fields and add AR/FR demo package translations

from django.db import migrations

TRANSLATABLE_PACKAGE_FIELDS = (
    'name', 'duration', 'short_description', 'full_description', 'itinerary', 'highlights',
)

PACKAGE_TRANSLATIONS = {
    'dubai-summer-package': {
        'name_ar': 'باقة دبي الصيفية',
        'name_fr': 'Forfait été Dubaï',
        'duration_ar': '5 أيام / 4 ليالٍ',
        'duration_fr': '5 jours / 4 nuits',
        'short_description_ar': (
            'استمتع بالتسوق الفاخر، رحلات السفاري الصحراوية، '
            'ومناظر أفق دبي الأيقونية.'
        ),
        'short_description_fr': (
            'Profitez du shopping de luxe, des safaris dans le désert '
            'et des vues emblématiques sur la skyline de Dubaï.'
        ),
    },
    'kuala-lumpur-honeymoon': {
        'name_ar': 'شهر عسل كوالالمبور',
        'name_fr': 'Lune de miel à Kuala Lumpur',
        'duration_ar': '7 أيام / 6 ليالٍ',
        'duration_fr': '7 jours / 6 nuits',
        'short_description_ar': (
            'عطلة رومانسية مع جولات في المدينة، معالم ثقافية، '
            'ومطاعم عالمية المستوى.'
        ),
        'short_description_fr': (
            'Une escapade romantique avec visites de la ville, '
            'sites culturels et gastronomie d\'exception.'
        ),
    },
    'paris-city-break': {
        'name_ar': 'عطلة باريس القصيرة',
        'name_fr': 'City break à Paris',
        'duration_ar': '4 أيام / 3 ليالٍ',
        'duration_fr': '4 jours / 3 nuits',
        'short_description_ar': (
            'اكتشف مدينة النور مع جولات مرشدة، متاحف، ومقاهٍ ساحرة.'
        ),
        'short_description_fr': (
            'Découvrez la Ville Lumière avec visites guidées, musées et cafés charmants.'
        ),
    },
    'bali-island-retreat': {
        'name_ar': 'استراحة جزيرة بالي',
        'name_fr': 'Retraite à Bali',
        'duration_ar': '8 أيام / 7 ليالٍ',
        'duration_fr': '8 jours / 7 nuits',
        'short_description_ar': (
            'استرخِ على الشواطئ الخلابة، واستكشف المعابد، '
            'واستمتع بكرم الضيافة البالي.'
        ),
        'short_description_fr': (
            'Détendez-vous sur des plages préservées, explorez les temples '
            'et profitez de l\'hospitalité balinaise.'
        ),
    },
    'istanbul-heritage-tour': {
        'name_ar': 'جولة إسطنبول التراثية',
        'name_fr': 'Circuit patrimoine Istanbul',
        'duration_ar': '6 أيام / 5 ليالٍ',
        'duration_fr': '6 jours / 5 nuits',
        'short_description_ar': (
            'تمشَّ عبر التاريخ حيث يلتقي الشرق بالغرب مع الأسواق والمساجد والمطبخ.'
        ),
        'short_description_fr': (
            'Parcourez l\'histoire là où l\'Orient rencontre l\'Occident : '
            'bazars, mosquées et gastronomie.'
        ),
    },
    'caribbean-beach-escape': {
        'name_ar': 'هروب إلى شواطئ الكاريبي',
        'name_fr': 'Évasion plage des Caraïbes',
        'duration_ar': '7 أيام / 6 ليالٍ',
        'duration_fr': '7 jours / 6 nuits',
        'short_description_ar': (
            'مياه فيروزية، شواطئ رملية بيضاء، واسترخاء لا يُنسى على الجزر.'
        ),
        'short_description_fr': (
            'Eaux turquoise, plages de sable blanc et détente insulaire inoubliable.'
        ),
    },
}


def copy_en_and_translate(apps, schema_editor):
    TravelPackage = apps.get_model('website', 'TravelPackage')
    Testimonial = apps.get_model('website', 'Testimonial')
    Destination = apps.get_model('website', 'Destination')
    VisaRequirement = apps.get_model('website', 'VisaRequirement')

    for pkg in TravelPackage.objects.all():
        changed = False
        for field in TRANSLATABLE_PACKAGE_FIELDS:
            base = getattr(pkg, field, None) or ''
            en_field = f'{field}_en'
            if base and not getattr(pkg, en_field, None):
                setattr(pkg, en_field, base)
                changed = True
        trans = PACKAGE_TRANSLATIONS.get(pkg.slug, {})
        for key, value in trans.items():
            setattr(pkg, key, value)
            changed = True
        if changed:
            pkg.save()

    for model, fields in (
        (Testimonial, ('content',)),
        (Destination, ('description',)),
        (VisaRequirement, ('country_name',)),
    ):
        for obj in model.objects.all():
            changed = False
            for field in fields:
                base = getattr(obj, field, None)
                en_field = f'{field}_en'
                if base and not getattr(obj, en_field, None):
                    setattr(obj, en_field, base)
                    changed = True
            if changed:
                obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_destination_description_ar_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_en_and_translate, migrations.RunPython.noop),
    ]
