# Generated manually for package image upload and price filtering

import re
from decimal import Decimal, InvalidOperation

import website.models
from django.db import migrations, models


def migrate_package_fields(apps, schema_editor):
    TravelPackage = apps.get_model('website', 'TravelPackage')
    for pkg in TravelPackage.objects.all():
        old_image = getattr(pkg, 'featured_image', '') or ''
        if isinstance(old_image, str) and old_image.startswith('http'):
            pkg.featured_image_url = old_image
            pkg.featured_image = ''

        old_price = getattr(pkg, 'price', '') or ''
        if old_price and not pkg.starting_price:
            numbers = re.findall(r'[\d,]+\.?\d*', str(old_price).replace(',', ''))
            if numbers:
                try:
                    pkg.starting_price = Decimal(numbers[0])
                except InvalidOperation:
                    pkg.starting_price = Decimal('0')
            else:
                pkg.starting_price = Decimal('0')

        if not pkg.starting_price:
            pkg.starting_price = Decimal('0')

        pkg.save(update_fields=['featured_image_url', 'starting_price', 'featured_image'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_visa_upload_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='travelpackage',
            name='featured_image_url',
            field=models.URLField(blank=True, help_text='Optional: image URL if you are not uploading a file', max_length=500),
        ),
        migrations.AddField(
            model_name='travelpackage',
            name='starting_price',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Starting price in USD (used for display and filtering)',
                max_digits=10,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(migrate_package_fields, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='travelpackage',
            name='price',
        ),
        migrations.AlterField(
            model_name='travelpackage',
            name='featured_image',
            field=models.ImageField(
                blank=True,
                help_text='Main package image',
                null=True,
                upload_to=website.models.package_image_path,
            ),
        ),
        migrations.AlterField(
            model_name='travelpackage',
            name='destination',
            field=models.CharField(help_text='Location, e.g. Dubai, UAE', max_length=120),
        ),
        migrations.AlterField(
            model_name='travelpackage',
            name='duration',
            field=models.CharField(help_text='e.g. 7 Days / 6 Nights', max_length=80),
        ),
        migrations.AlterField(
            model_name='travelpackage',
            name='name',
            field=models.CharField(help_text='Package title shown on the website', max_length=200),
        ),
        migrations.AlterField(
            model_name='travelpackage',
            name='short_description',
            field=models.TextField(help_text='Short description on the package card'),
        ),
    ]
