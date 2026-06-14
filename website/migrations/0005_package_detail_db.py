"""Idempotent database changes for package detail fields (runs before 0004 state)."""

from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    TravelPackage = apps.get_model('website', 'TravelPackage')
    table = TravelPackage._meta.db_table
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f'SELECT id, name, slug FROM {table}')
        rows = cursor.fetchall()

    used = set()
    updates = []
    for pk, name, slug in rows:
        if slug:
            used.add(slug)
            continue
        base = slugify(name) or 'package'
        new_slug = base
        counter = 1
        while new_slug in used:
            new_slug = f'{base}-{counter}'
            counter += 1
        used.add(new_slug)
        updates.append((new_slug, pk))

    with schema_editor.connection.cursor() as cursor:
        for new_slug, pk in updates:
            cursor.execute(f'UPDATE {table} SET slug = %s WHERE id = %s', [new_slug, pk])


def apply_postgres(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('DROP INDEX IF EXISTS website_travelpackage_slug_d02ee58c_like')
        cursor.execute('DROP INDEX IF EXISTS website_travelpackage_slug_d02ee58c')
        cursor.execute('DROP INDEX IF EXISTS website_travelpackage_slug_key')

        cursor.execute(
            'ALTER TABLE website_travelpackage '
            "ADD COLUMN IF NOT EXISTS full_description text NOT NULL DEFAULT ''"
        )
        cursor.execute(
            'ALTER TABLE website_travelpackage '
            "ADD COLUMN IF NOT EXISTS highlights text NOT NULL DEFAULT ''"
        )
        cursor.execute(
            'ALTER TABLE website_travelpackage '
            "ADD COLUMN IF NOT EXISTS itinerary text NOT NULL DEFAULT ''"
        )
        cursor.execute(
            'ALTER TABLE website_travelpackage '
            "ADD COLUMN IF NOT EXISTS slug varchar(220) NOT NULL DEFAULT ''"
        )

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS website_packageimage (
                id bigserial PRIMARY KEY,
                image varchar(100),
                external_image_url varchar(500) NOT NULL DEFAULT '',
                caption varchar(200) NOT NULL DEFAULT '',
                display_order integer NOT NULL CHECK (display_order >= 0),
                package_id bigint NOT NULL REFERENCES website_travelpackage(id)
                    DEFERRABLE INITIALLY DEFERRED
            )
        ''')

    populate_slugs(apps, schema_editor)

    with schema_editor.connection.cursor() as cursor:
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS website_travelpackage_slug_key
            ON website_travelpackage (slug)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS website_travelpackage_slug_d02ee58c_like
            ON website_travelpackage (slug varchar_pattern_ops)
        ''')


def _sqlite_text_field(name):
    field = models.TextField(blank=True, default='')
    field.set_attributes_from_name(name)
    return field


def _sqlite_slug_field():
    field = models.SlugField(max_length=220, blank=True, default='')
    field.set_attributes_from_name('slug')
    return field


def apply_sqlite(apps, schema_editor):
    """0005 runs before 0004 state — define fields explicitly, not via historical model."""
    TravelPackage = apps.get_model('website', 'TravelPackage')

    with schema_editor.connection.cursor() as cursor:
        cursor.execute('PRAGMA table_info(website_travelpackage)')
        columns = {row[1] for row in cursor.fetchall()}

    if 'full_description' not in columns:
        schema_editor.add_field(TravelPackage, _sqlite_text_field('full_description'))
    if 'highlights' not in columns:
        schema_editor.add_field(TravelPackage, _sqlite_text_field('highlights'))
    if 'itinerary' not in columns:
        schema_editor.add_field(TravelPackage, _sqlite_text_field('itinerary'))
    if 'slug' not in columns:
        schema_editor.add_field(TravelPackage, _sqlite_slug_field())
        populate_slugs(apps, schema_editor)
        slug_field = _sqlite_slug_field()
        slug_field.unique = True
        schema_editor.alter_field(TravelPackage, _sqlite_slug_field(), slug_field, strict=False)
    else:
        populate_slugs(apps, schema_editor)

    tables = schema_editor.connection.introspection.table_names()
    if 'website_packageimage' not in tables:
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE website_packageimage (
                    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    image varchar(100),
                    external_image_url varchar(500) NOT NULL,
                    caption varchar(200) NOT NULL,
                    display_order integer unsigned NOT NULL CHECK (display_order >= 0),
                    package_id bigint NOT NULL REFERENCES website_travelpackage(id)
                )
            ''')


def apply_db_changes(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        apply_postgres(apps, schema_editor)
    else:
        apply_sqlite(apps, schema_editor)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_package_image_and_price_filter'),
    ]

    run_before = [
        ('website', '0004_package_detail_and_gallery'),
    ]

    operations = [
        migrations.RunPython(apply_db_changes, migrations.RunPython.noop),
    ]
