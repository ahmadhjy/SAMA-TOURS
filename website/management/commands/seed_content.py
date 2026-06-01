from django.core.management.base import BaseCommand
from website.models import TravelPackage, Destination, VisaRequirement, Testimonial


class Command(BaseCommand):
    help = 'Seed sample packages, destinations, visas, and testimonials'

    def handle(self, *args, **options):
        if TravelPackage.objects.exists():
            self.stdout.write(self.style.WARNING('Content already exists. Skipping seed.'))
            return

        packages = [
            {
                'name': 'Dubai Summer Package',
                'destination': 'Dubai, UAE',
                'duration': '5 Days / 4 Nights',
                'starting_price': 899,
                'short_description': 'Experience luxury shopping, desert safaris, and iconic skyline views in Dubai.',
                'featured_image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
                'display_order': 1,
            },
            {
                'name': 'Kuala Lumpur Honeymoon',
                'destination': 'Kuala Lumpur, Malaysia',
                'duration': '7 Days / 6 Nights',
                'starting_price': 1199,
                'short_description': 'A romantic escape with city tours, cultural landmarks, and world-class dining.',
                'featured_image_url': 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&q=80',
                'display_order': 2,
            },
            {
                'name': 'Paris City Break',
                'destination': 'Paris, France',
                'duration': '4 Days / 3 Nights',
                'starting_price': 1050,
                'short_description': 'Discover the City of Light with guided tours, museums, and charming cafés.',
                'featured_image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
                'display_order': 3,
            },
            {
                'name': 'Bali Island Retreat',
                'destination': 'Bali, Indonesia',
                'duration': '8 Days / 7 Nights',
                'starting_price': 1350,
                'short_description': 'Relax on pristine beaches, explore temples, and enjoy Balinese hospitality.',
                'featured_image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80',
                'display_order': 4,
            },
            {
                'name': 'Istanbul Heritage Tour',
                'destination': 'Istanbul, Turkey',
                'duration': '6 Days / 5 Nights',
                'starting_price': 780,
                'short_description': 'Walk through history where East meets West with bazaars, mosques, and cuisine.',
                'featured_image_url': 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800&q=80',
                'display_order': 5,
            },
            {
                'name': 'Caribbean Beach Escape',
                'destination': 'Antigua & Barbuda',
                'duration': '7 Days / 6 Nights',
                'starting_price': 1450,
                'short_description': 'Turquoise waters, white-sand beaches, and unforgettable island relaxation.',
                'featured_image_url': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80',
                'display_order': 6,
            },
        ]
        for data in packages:
            TravelPackage.objects.create(**data)

        destinations = [
            ('Dubai', 'United Arab Emirates', 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80'),
            ('Paris', 'France', 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=600&q=80'),
            ('Tokyo', 'Japan', 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&q=80'),
            ('Bali', 'Indonesia', 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=600&q=80'),
            ('Rome', 'Italy', 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&q=80'),
            ('Barcelona', 'Spain', 'https://images.unsplash.com/photo-1583422409513-0b228e0c9ad1?w=600&q=80'),
            ('Maldives', 'Maldives', 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=600&q=80'),
            ('Istanbul', 'Turkey', 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&q=80'),
        ]
        for i, (name, country, img) in enumerate(destinations, 1):
            Destination.objects.create(
                name=name,
                country=country,
                featured_image=img,
                description=f'Explore {name} with expertly curated itineraries from Sama Tours.',
                display_order=i,
            )

        visas = [
            ('United Arab Emirates', 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&q=80'),
            ('Turkey', 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&q=80'),
            ('Schengen (Europe)', 'https://images.unsplash.com/photo-1467269209838-890b6a69d093?w=600&q=80'),
            ('United Kingdom', 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&q=80'),
            ('United States', 'https://images.unsplash.com/photo-1485738422979-f5c462d49f74?w=600&q=80'),
            ('Canada', 'https://images.unsplash.com/photo-1519832979-6fa567b78160?w=600&q=80'),
            ('Australia', 'https://images.unsplash.com/photo-1523482580675-f109ba2629?w=600&q=80'),
            ('Thailand', 'https://images.unsplash.com/photo-1552465011-b4e21bf6e79d?w=600&q=80'),
        ]
        for i, (country, img) in enumerate(visas, 1):
            VisaRequirement.objects.create(
                country_name=country,
                featured_image_url=img,
                display_order=i,
            )

        testimonials = [
            {
                'author_name': 'DODO HB',
                'content': (
                    'We had the most unforgettable honeymoon in Kuala Lumpur, all thanks to Sama Tours. '
                    'From the moment we reached out, their team was professional, attentive, and '
                    'incredibly helpful in planning every detail.'
                ),
                'display_order': 1,
            },
            {
                'author_name': 'Mariam Haidar',
                'content': (
                    'Thank you, Sama Tours team, for your exceptional service! Your professionalism and '
                    'attention to detail made my experience seamless and enjoyable. Highly recommended.'
                ),
                'display_order': 2,
            },
            {
                'author_name': 'Nourhanne Aoun',
                'content': (
                    'The travel agents are so helpful. After doing a very long research, Sama Tours was '
                    'our perfect choice. They answered our hundred questions and they were super fast in '
                    'finding us the package that fits us most.'
                ),
                'display_order': 3,
            },
        ]
        for data in testimonials:
            Testimonial.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully seeded website content.'))
