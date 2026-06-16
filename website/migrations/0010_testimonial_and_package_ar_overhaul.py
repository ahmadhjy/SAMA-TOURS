# Testimonial + TravelPackage Arabic copy overhaul
#
# Fixes cases where only the first testimonial shows in Arabic by updating all
# testimonial translation fields using resilient author-name matching.
# Also aligns displayed Arabic package cards with the latest homepage reference.

import re

from django.db import migrations


def normalize_author(name: str) -> str:
    return re.sub(r"\s+", " ", (name or "")).strip().lower()


TESTIMONIAL_TRANSLATIONS = {
    # Reference Arabic copy from the user.
    "dodo hb": {
        "content_ar": (
            "كانت رحلة شهر العسل إلى كوالالمبور من أجمل التجارب، "
            "وكل ذلك بفضل سما تورز. منذ أول تواصل، كان الفريق محترفًا، "
            "متعاونًا، واهتم بكل التفاصيل."
        ),
        "content_fr": (
            "Nous avons passé une lune de miel inoubliable à Kuala Lumpur grâce à Sama Tours. "
            "Dès notre premier contact, l'équipe a été professionnelle, attentive et "
            "très efficace pour organiser chaque détail."
        ),
    },
    "mariam haidar": {
        "content_ar": (
            "شكرًا لفريق سما تورز على الخدمة الرائعة! "
            "الاحترافية والاهتمام بالتفاصيل جعلوا تجربتي سهلة وممتعة. "
            "أنصح بهم بكل ثقة."
        ),
        "content_fr": (
            "Merci à l'équipe Sama Tours pour un service exceptionnel ! "
            "Leur professionnalisme et leur souci du détail ont rendu mon expérience fluide et agréable. "
            "Je recommande vivement."
        ),
    },
    "nourhanne aoun": {
        "content_ar": (
            "فريق السفر لديهم متعاون جدًا. بعد بحث طويل، كان اختيار سما تورز هو الأفضل. "
            "أجابوا على كل أسئلتنا بسرعة وساعدونا في إيجاد الباقة الأنسب لنا."
        ),
        "content_fr": (
            "Les conseillers sont très à l'écoute. Après de longues recherches, "
            "Sama Tours a été le bon choix : réponses rapides et forfait parfaitement adapté à nos besoins."
        ),
    },
}


PACKAGE_AR_OVERRIDES = {
    "dubai-summer-package": {
        "name_ar": "باقة صيف دبي",
        "duration_ar": "5 أيام / 4 ليالٍ",
        "short_description_ar": (
            "استمتع بالتسوّق الفاخر، رحلات السفاري الصحراوية، وإطلالات دبي الشهيرة."
        ),
    },
    "kuala-lumpur-honeymoon": {
        "name_ar": "شهر عسل في كوالالمبور",
        "duration_ar": "7 أيام / 6 ليالٍ",
        "short_description_ar": (
            "رحلة رومانسية تجمع بين الجولات السياحية، المعالم الثقافية، وتجارب الطعام المميزة."
        ),
    },
    "paris-city-break": {
        "name_ar": "عطلة قصيرة في باريس",
        "duration_ar": "4 أيام / 3 ليالٍ",
        "short_description_ar": (
            "اكتشف مدينة النور من خلال الجولات، المتاحف، والمقاهي الباريسية الساحرة."
        ),
    },
    "bali-island-retreat": {
        "name_ar": "استراحة جزيرة بالي",
        "duration_ar": "8 أيام / 7 ليالٍ",
        "short_description_ar": (
            "استرخِ على الشواطئ، زر المعابد، واستمتع بكرم الضيافة البالية."
        ),
    },
    "istanbul-heritage-tour": {
        "name_ar": "جولة إسطنبول التراثية",
        "duration_ar": "6 أيام / 5 ليالٍ",
        "short_description_ar": (
            "تنقّل بين التاريخ والثقافة حيث يلتقي الشرق بالغرب، من الأسواق إلى المساجد والمأكولات."
        ),
    },
    "caribbean-beach-escape": {
        "name_ar": "هروب إلى شواطئ الكاريبي",
        "duration_ar": "7 أيام / 6 ليالٍ",
        "short_description_ar": (
            "مياه فيروزية، رمال بيضاء، وأجواء جزيرة مثالية للاسترخاء."
        ),
    },
}


def apply_overrides(apps, schema_editor):
    Testimonial = apps.get_model("website", "Testimonial")
    TravelPackage = apps.get_model("website", "TravelPackage")

    for testimonial in Testimonial.objects.all():
        author_key = normalize_author(testimonial.author_name)

        trans = None
        if author_key in TESTIMONIAL_TRANSLATIONS:
            trans = TESTIMONIAL_TRANSLATIONS[author_key]
        else:
            # Resilient fallback for minor spelling/spacing differences.
            if "dodo" in author_key:
                trans = TESTIMONIAL_TRANSLATIONS["dodo hb"]
            elif "mariam" in author_key or "haidar" in author_key:
                trans = TESTIMONIAL_TRANSLATIONS["mariam haidar"]
            elif "nourhanne" in author_key or "aoun" in author_key:
                trans = TESTIMONIAL_TRANSLATIONS["nourhanne aoun"]

        if not trans:
            continue

        for field, value in trans.items():
            setattr(testimonial, field, value)
        testimonial.save(update_fields=list(trans.keys()))

    for pkg in TravelPackage.objects.all():
        overrides = PACKAGE_AR_OVERRIDES.get(pkg.slug)
        if not overrides:
            continue
        for field, value in overrides.items():
            setattr(pkg, field, value)
        pkg.save(update_fields=list(overrides.keys()))


class Migration(migrations.Migration):
    dependencies = [
        ("website", "0009_testimonial_translations"),
    ]

    operations = [
        migrations.RunPython(apply_overrides, migrations.RunPython.noop),
    ]

