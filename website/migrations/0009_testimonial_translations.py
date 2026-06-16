# Testimonial translations + refined Arabic package copy

from django.db import migrations

TESTIMONIAL_TRANSLATIONS = {
    'DODO HB': {
        'content_ar': (
            'قضينا شهر عسل لا يُنسى في كوالالمبور بفضل سما تورز. '
            'منذ أول تواصل معنا، كان الفريق محترفاً ومهتماً بكل التفاصيل '
            'وساعدنا في ترتيب الرحلة بالكامل.'
        ),
        'content_fr': (
            'Nous avons passé une lune de miel inoubliable à Kuala Lumpur grâce à Sama Tours. '
            'Dès notre premier contact, l\'équipe a été professionnelle, attentive et '
            'très efficace pour organiser chaque détail.'
        ),
    },
    'Mariam Haidar': {
        'content_ar': (
            'شكراً لفريق سما تورز على الخدمة المميّزة! '
            'الاحترافية والاهتمام بالتفاصيل جعلوا تجربتي سلسة وممتعة. أنصح بهم بقوة.'
        ),
        'content_fr': (
            'Merci à l\'équipe Sama Tours pour un service exceptionnel ! '
            'Leur professionnalisme et leur souci du détail ont rendu mon expérience fluide et agréable. '
            'Je recommande vivement.'
        ),
    },
    'Nourhanne Aoun': {
        'content_ar': (
            'فريق العمل متعاون جداً. بعد بحث طويل، اخترنا سما تورز وكان القرار الصحيح. '
            'أجابوا على كل استفساراتنا بسرعة ووفّروا لنا الباقة الأنسب.'
        ),
        'content_fr': (
            'Les conseillers sont très à l\'écoute. Après de longues recherches, '
            'Sama Tours a été le bon choix : réponses rapides et forfait parfaitement adapté à nos besoins.'
        ),
    },
}

PACKAGE_AR_REFINEMENTS = {
    'dubai-summer-package': {
        'short_description_ar': (
            'تسوّق فاخر، سفاري صحراوي، وأفضل معالم دبي في باقة واحدة.'
        ),
    },
    'kuala-lumpur-honeymoon': {
        'name_ar': 'شهر عسل في كوالالمبور',
        'short_description_ar': (
            'رحلة رومانسية تجمع بين جولات المدينة والمعالم الثقافية وأشهى المطاعم.'
        ),
    },
    'paris-city-break': {
        'name_ar': 'عطلة قصيرة في باريس',
        'short_description_ar': (
            'اكتشف باريس مع جولات مرشدة، متاحف عالمية، وأجواء المقاهي الفرنسية.'
        ),
    },
    'bali-island-retreat': {
        'short_description_ar': (
            'استرخِ على شواطئ خلابة، زُر المعابد، واستمتع بكرم الضيافة البالية.'
        ),
    },
    'istanbul-heritage-tour': {
        'short_description_ar': (
            'اكتشف إسطنبول حيث يلتقي الشرق بالغرب: أسواق تاريخية، مساجد، ومأكولات مميّزة.'
        ),
    },
    'caribbean-beach-escape': {
        'name_ar': 'عطلة شاطئية في الكاريبي',
        'short_description_ar': (
            'مياه زرقاء صافية، شواطئ رملية بيضاء، واسترخاء لا يُنسى.'
        ),
    },
}


def apply_translations(apps, schema_editor):
    Testimonial = apps.get_model('website', 'Testimonial')
    TravelPackage = apps.get_model('website', 'TravelPackage')

    for testimonial in Testimonial.objects.all():
        trans = TESTIMONIAL_TRANSLATIONS.get(testimonial.author_name)
        if not trans:
            continue
        for field, value in trans.items():
            setattr(testimonial, field, value)
        testimonial.save()

    for pkg in TravelPackage.objects.all():
        updates = PACKAGE_AR_REFINEMENTS.get(pkg.slug, {})
        if not updates:
            continue
        for field, value in updates.items():
            setattr(pkg, field, value)
        pkg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_package_translations'),
    ]

    operations = [
        migrations.RunPython(apply_translations, migrations.RunPython.noop),
    ]
