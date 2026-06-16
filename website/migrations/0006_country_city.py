# Generated manually — split destination into country + city

from django.db import migrations, models

from website.countries import COUNTRY_CHOICES, parse_legacy_destination


def forwards(apps, schema_editor):
    TravelPackage = apps.get_model('website', 'TravelPackage')
    for pkg in TravelPackage.objects.all():
        dest = getattr(pkg, 'destination', '') or ''
        city, country = parse_legacy_destination(dest)
        pkg.city = city
        pkg.country = country
        pkg.save(update_fields=['city', 'country'])


def backwards(apps, schema_editor):
    TravelPackage = apps.get_model('website', 'TravelPackage')
    for pkg in TravelPackage.objects.all():
        if pkg.city:
            pkg.destination = f'{pkg.city}, {pkg.country}'
        else:
            pkg.destination = pkg.country
        pkg.save(update_fields=['destination'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_package_detail_and_gallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelpackage',
            name='city',
            field=models.CharField(blank=True, help_text='City or region (e.g. Dubai)', max_length=120),
        ),
        migrations.AddField(
            model_name='travelpackage',
            name='country',
            field=models.CharField(
                choices=COUNTRY_CHOICES,
                default='Lebanon',
                help_text='Destination country',
                max_length=120,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(
            model_name='travelpackage',
            name='destination',
        ),
    ]
