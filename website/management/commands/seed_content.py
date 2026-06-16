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
                'name_en': 'Dubai Summer Package',
                'country': 'United Arab Emirates',
                'city': 'Dubai',
                'duration_en': '5 Days / 4 Nights',
                'starting_price': 899,
                'short_description_en': (
                    'Experience luxury shopping, desert safaris, and iconic skyline views in Dubai.'
                ),
                'featured_image_url': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=800&q=80',
                'display_order': 1,
            },
            {
                'name_en': 'Kuala Lumpur Honeymoon',
                'country': 'Malaysia',
                'city': 'Kuala Lumpur',
                'duration_en': '7 Days / 6 Nights',
                'starting_price': 1199,
                'short_description_en': (
                    'A romantic escape with city tours, cultural landmarks, and world-class dining.'
                ),
                'featured_image_url': 'https://images.unsplash.com/photo-1596422846543-75c6fc197f07?w=800&q=80',
                'display_order': 2,
            },
            {
                'name_en': 'Paris City Break',
                'country': 'France',
                'city': 'Paris',
                'duration_en': '4 Days / 3 Nights',
                'starting_price': 1050,
                'short_description_en': (
                    'Discover the City of Light with guided tours, museums, and charming cafés.'
                ),
                'featured_image_url': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&q=80',
                'display_order': 3,
            },
            {
                'name_en': 'Bali Island Retreat',
                'country': 'Indonesia',
                'city': 'Bali',
                'duration_en': '8 Days / 7 Nights',
                'starting_price': 1350,
                'short_description_en': (
                    'Relax on pristine beaches, explore temples, and enjoy Balinese hospitality.'
                ),
                'featured_image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80',
                'display_order': 4,
            },
            {
                'name_en': 'Istanbul Heritage Tour',
                'country': 'Turkey',
                'city': 'Istanbul',
                'duration_en': '6 Days / 5 Nights',
                'starting_price': 780,
                'short_description_en': (
                    'Walk through history where East meets West with bazaars, mosques, and cuisine.'
                ),
                'featured_image_url': 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=800&q=80',
                'display_order': 5,
            },
            {
                'name_en': 'Caribbean Beach Escape',
                'country': 'Antigua and Barbuda',
                'city': '',
                'duration_en': '7 Days / 6 Nights',
                'starting_price': 1450,
                'short_description_en': (
                    'Turquoise waters, white-sand beaches, and unforgettable island relaxation.'
                ),
                'featured_image_url': 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80',
                'display_order': 6,
            },
        ]
        translations = {
            'Dubai Summer Package': {
                'name_ar': 'باقة دبي الصيفية', 'name_fr': 'Forfait été Dubaï',
                'duration_ar': '5 أيام / 4 ليالٍ', 'duration_fr': '5 jours / 4 nuits',
                'short_description_ar': 'استمتع بالتسوق الفاخر، رحلات السفاري الصحراوية، ومناظر أفق دبي الأيقونية.',
                'short_description_fr': 'Profitez du shopping de luxe, des safaris dans le désert et des vues emblématiques sur la skyline de Dubaï.',
            },
            'Kuala Lumpur Honeymoon': {
                'name_ar': 'شهر عسل كوالالمبور', 'name_fr': 'Lune de miel à Kuala Lumpur',
                'duration_ar': '7 أيام / 6 ليالٍ', 'duration_fr': '7 jours / 6 nuits',
                'short_description_ar': 'عطلة رومانسية مع جولات في المدينة، معالم ثقافية، ومطاعم عالمية المستوى.',
                'short_description_fr': 'Une escapade romantique avec visites de la ville, sites culturels et gastronomie d\'exception.',
            },
            'Paris City Break': {
                'name_ar': 'عطلة باريس القصيرة', 'name_fr': 'City break à Paris',
                'duration_ar': '4 أيام / 3 ليالٍ', 'duration_fr': '4 jours / 3 nuits',
                'short_description_ar': 'اكتشف مدينة النور مع جولات مرشدة، متاحف، ومقاهٍ ساحرة.',
                'short_description_fr': 'Découvrez la Ville Lumière avec visites guidées, musées et cafés charmants.',
            },
            'Bali Island Retreat': {
                'name_ar': 'استراحة جزيرة بالي', 'name_fr': 'Retraite à Bali',
                'duration_ar': '8 أيام / 7 ليالٍ', 'duration_fr': '8 jours / 7 nuits',
                'short_description_ar': 'استرخِ على الشواطئ الخلابة، واستكشف المعابد، واستمتع بكرم الضيافة البالي.',
                'short_description_fr': 'Détendez-vous sur des plages préservées, explorez les temples et profitez de l\'hospitalité balinaise.',
            },
            'Istanbul Heritage Tour': {
                'name_ar': 'جولة إسطنبول التراثية', 'name_fr': 'Circuit patrimoine Istanbul',
                'duration_ar': '6 أيام / 5 ليالٍ', 'duration_fr': '6 jours / 5 nuits',
                'short_description_ar': 'تمشَّ عبر التاريخ حيث يلتقي الشرق بالغرب مع الأسواق والمساجد والمطبخ.',
                'short_description_fr': 'Parcourez l\'histoire là où l\'Orient rencontre l\'Occident : bazars, mosquées et gastronomie.',
            },
            'Caribbean Beach Escape': {
                'name_ar': 'هروب إلى شواطئ الكاريبي', 'name_fr': 'Évasion plage des Caraïbes',
                'duration_ar': '7 أيام / 6 ليالٍ', 'duration_fr': '7 jours / 6 nuits',
                'short_description_ar': 'مياه فيروزية، شواطئ رملية بيضاء، واسترخاء لا يُنسى على الجزر.',
                'short_description_fr': 'Eaux turquoise, plages de sable blanc et détente insulaire inoubliable.',
            },
        }
        for data in packages:
            en_name = data.pop('name_en')
            extra = translations.get(en_name, {})
            TravelPackage.objects.create(name_en=en_name, **data, **extra)

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
                description_en=f'Explore {name} with expertly curated itineraries from Sama Tours.',
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
                country_name_en=country,
                featured_image_url=img,
                display_order=i,
            )

        testimonials = [
            {
                'author_name': 'DODO HB',
                'content_en': (
                    'We had the most unforgettable honeymoon in Kuala Lumpur, all thanks to Sama Tours. '
                    'From the moment we reached out, their team was professional, attentive, and '
                    'incredibly helpful in planning every detail.'
                ),
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
                'display_order': 1,
            },
            {
                'author_name': 'Mariam Haidar',
                'content_en': (
                    'Thank you, Sama Tours team, for your exceptional service! Your professionalism and '
                    'attention to detail made my experience seamless and enjoyable. Highly recommended.'
                ),
                'content_ar': (
                    'شكراً لفريق سما تورز على الخدمة المميّزة! '
                    'الاحترافية والاهتمام بالتفاصيل جعلوا تجربتي سلسة وممتعة. أنصح بهم بقوة.'
                ),
                'content_fr': (
                    'Merci à l\'équipe Sama Tours pour un service exceptionnel ! '
                    'Leur professionnalisme et leur souci du détail ont rendu mon expérience fluide et agréable. '
                    'Je recommande vivement.'
                ),
                'display_order': 2,
            },
            {
                'author_name': 'Nourhanne Aoun',
                'content_en': (
                    'The travel agents are so helpful. After doing a very long research, Sama Tours was '
                    'our perfect choice. They answered our hundred questions and they were super fast in '
                    'finding us the package that fits us most.'
                ),
                'content_ar': (
                    'فريق العمل متعاون جداً. بعد بحث طويل، اخترنا سما تورز وكان القرار الصحيح. '
                    'أجابوا على كل استفساراتنا بسرعة ووفّروا لنا الباقة الأنسب.'
                ),
                'content_fr': (
                    'Les conseillers sont très à l\'écoute. Après de longues recherches, '
                    'Sama Tours a été le bon choix : réponses rapides et forfait parfaitement adapté à nos besoins.'
                ),
                'display_order': 3,
            },
        ]
        for data in testimonials:
            Testimonial.objects.create(**data)

        self.stdout.write(self.style.SUCCESS('Successfully seeded website content.'))
