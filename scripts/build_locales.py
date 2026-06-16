#!/usr/bin/env python
"""Build django.mo files from embedded AR/FR translations (no gettext tools required)."""

from pathlib import Path

try:
    import polib
except ImportError:
    raise SystemExit('Install polib: pip install polib')

BASE = Path(__file__).resolve().parent.parent / 'locale'

# msgid -> (ar, fr)
MESSAGES = {
    'Sama Tours': ('سما تورز', 'Sama Tours'),
    'Sama Tours Lebanon': ('سما تورز لبنان', 'Sama Tours Liban'),
    'Home': ('الرئيسية', 'Accueil'),
    'About': ('من نحن', 'À propos'),
    'Packages': ('الباقات', 'Forfaits'),
    'Visa Requirements': ('متطلبات التأشيرات', 'Exigences de visa'),
    'Contact Us': ('تواصل معنا', 'Contactez-nous'),
    'Contact': ('اتصل', 'Contact'),
    'Language': ('اللغة', 'Langue'),
    'Toggle navigation': ('فتح القائمة', 'Basculer la navigation'),
    'Sama Tours — Home': ('سما تورز — الرئيسية', 'Sama Tours — Accueil'),
    'Mon – Sun, 9:00 – 18:00': ('الإثنين – الأحد، 9:00 صباحًا – 6:00 مساءً', 'Lun – Dim, 9h00 – 18h00'),
    'WhatsApp': ('واتساب', 'WhatsApp'),
    'Travel beyond your imagination, with Sama Tours!': (
        'سافر أبعد من خيالك مع سما تورز!',
        'Voyagez au-delà de votre imagination avec Sama Tours !',
    ),
    'Chat on WhatsApp': ('تحدث معنا عبر واتساب', 'Discuter sur WhatsApp'),
    'Quick Links': ('روابط سريعة', 'Liens rapides'),
    'Follow Us': ('تابعونا', 'Suivez-nous'),
    'All rights reserved.': ('جميع الحقوق محفوظة.', 'Tous droits réservés.'),
    'Facebook': ('فيسبوك', 'Facebook'),
    'Instagram': ('إنستغرام', 'Instagram'),
    'Why book with Sama Tours': ('لماذا تحجز مع سما تورز', 'Pourquoi réserver avec Sama Tours'),
    'Expert Travel Agents': ('خبراء سفر', 'Agents de voyage experts'),
    'Personal planning for every trip': ('تخطيط شخصي يناسب كل رحلة', 'Planification personnalisée pour chaque voyage'),
    'Book via WhatsApp': ('حجز سريع عبر واتساب', 'Réserver via WhatsApp'),
    'Fast quotes & easy booking': ('عروض أسعار سريعة وحجز بسهولة', 'Devis rapides et réservation facile'),
    'Visa Services': ('خدمات التأشيرات', 'Services de visa'),
    'Visa services': ('خدمات التأشيرات', 'Services de visa'),
    'Requirements & documentation': ('إرشاد كامل حول المتطلبات والمستندات', 'Exigences et documentation'),
    'Affordable Packages': ('باقات بأسعار مناسبة', 'Forfaits voyage abordables'),
    'Dream vacations within budget': ('عطلات مميزة ضمن ميزانيتك', 'Vacances de rêve dans votre budget'),
    'View details': ('عرض التفاصيل', 'Voir les détails'),
    'Book Now': ('احجز الآن', 'Réserver'),
    'Find your perfect trip': ('اختر الرحلة الأنسب لك', 'Trouvez votre voyage idéal'),
    'Filter by country and budget': ('تصفية حسب الدولة والميزانية', 'Filtrer par pays et budget'),
    'Country': ('الدولة', 'Pays'),
    'All countries': ('جميع الدول', 'Tous les pays'),
    'Budget': ('الميزانية', 'Budget'),
    'Search': ('بحث', 'Rechercher'),
    'Clear': ('مسح', 'Effacer'),
    'Any price': ('أي سعر', 'Tout prix'),
    'Up to $500': ('حتى 500$', 'Jusqu\'à 500 $'),
    'Up to $1,000': ('حتى 1,000$', 'Jusqu\'à 1 000 $'),
    'Up to $1,500': ('حتى 1,500$', 'Jusqu\'à 1 500 $'),
    'Up to $2,000': ('حتى 2,000$', 'Jusqu\'à 2 000 $'),
    'Up to $5,000': ('حتى 5,000$', 'Jusqu\'à 5 000 $'),
    'Up to $10,000': ('حتى 10,000$', 'Jusqu\'à 10 000 $'),
    'Your journey starts here': ('رحلتك تبدأ من هنا', 'Votre voyage commence ici'),
    'Explore the World with Sama Tours': ('اكتشف العالم مع سما تورز', 'Explorez le monde avec Sama Tours'),
    'Book packages, plan custom trips, and get visa support — all with experienced travel experts by your side.': (
        'احجز باقات سفر جاهزة، خطّط رحلتك الخاصة، واحصل على دعم كامل في معاملات التأشيرة — مع فريق سفر خبير يرافقك في كل خطوة.',
        'Réservez des forfaits, planifiez des voyages sur mesure et obtenez un soutien visa — avec des experts à vos côtés.',
    ),
    'Book Your Trip': ('احجز رحلتك', 'Réservez votre voyage'),
    'Get a Quote': ('اطلب عرض سعر', 'Demander un devis'),
    'Travel deals & inspiration': ('عروض سفر وإلهام لرحلتك القادمة', 'Offres et inspiration voyage'),
    'Handpicked offers to help you plan your next getaway': (
        'اختيارات مميزة تساعدك على التخطيط لعطلتك المقبلة',
        'Offres sélectionnées pour planifier votre prochaine escapade',
    ),
    'View all packages': ('عرض كل الباقات', 'Voir tous les forfaits'),
    'Popular': ('الأكثر طلبًا', 'Populaire'),
    'Beach & Sun Escapes': ('عروض الشواطئ والعطلات', 'Évasions plage et soleil'),
    'Caribbean, Maldives & more — relax by the sea': (
        'الكاريبي، المالديف والمزيد — استرخِ على أجمل الشواطئ',
        'Caraïbes, Maldives et plus — détente au bord de la mer',
    ),
    'Discover deals': ('اكتشف العروض', 'Découvrir les offres'),
    'City breaks': ('رحلات المدن', 'City breaks'),
    'Europe & Beyond': ('أوروبا وما حولها', 'Europe et au-delà'),
    'Paris, Dubai, Istanbul & iconic destinations': (
        'باريس، دبي، إسطنبول ووجهات عالمية لا تُنسى',
        'Paris, Dubaï, Istanbul et destinations emblématiques',
    ),
    'Country guides & PDF documents in one place': (
        'إرشادات حسب الدولة وملفات PDF في مكان واحد',
        'Guides par pays et documents PDF en un seul endroit',
    ),
    'View documents': ('عرض المستندات', 'Voir les documents'),
    'We love travel — discover top destinations': (
        'نحب السفر — اكتشف أجمل الوجهات',
        'Nous aimons voyager — découvrez les meilleures destinations',
    ),
    'From beaches to cities, find your perfect holiday spot': (
        'من الشواطئ الهادئة إلى المدن النابضة بالحياة، اختر الوجهة التي تناسبك',
        'Des plages aux villes, trouvez votre lieu de vacances idéal',
    ),
    'Book now': ('احجز الآن', 'Réserver'),
    'Affordable travel packages': ('باقات سفر بأسعار مدروسة', 'Forfaits voyage abordables'),
    'Everyone deserves their dream vacation — browse and book on WhatsApp': (
        'لأن كل شخص يستحق إجازة الأحلام — تصفح الباقات واحجز عبر واتساب',
        'Chacun mérite ses vacances de rêve — parcourez et réservez sur WhatsApp',
    ),
    'All packages': ('كل الباقات', 'Tous les forfaits'),
    'The Sama Tours promise': ('وعد سما تورز', 'La promesse Sama Tours'),
    'Everything you need for a worry-free holiday — from one trusted team': (
        'كل ما تحتاجه لعطلة مريحة — مع فريق واحد تثق به',
        'Tout pour des vacances sans souci — une seule équipe de confiance',
    ),
    'All in one place': ('كل شيء في مكان واحد', 'Tout en un seul endroit'),
    'Flights, hotels, itineraries, insurance & local guides — planned together.': (
        'رحلات الطيران، الفنادق، البرامج، التأمين والمرشدون المحليون — بتنسيق كامل.',
        'Vols, hôtels, itinéraires, assurance et guides locaux — planifiés ensemble.',
    ),
    'Expert advice': ('استشارة خبيرة', 'Conseils d\'experts'),
    'Knowledgeable agents tailor every trip to your budget and preferences.': (
        'فريقنا يساعدك على اختيار الرحلة الأنسب لميزانيتك واهتماماتك.',
        'Des agents compétents adaptent chaque voyage à votre budget et vos préférences.',
    ),
    'Always reachable': ('دائمًا بالقرب منك', 'Toujours joignables'),
    'Quick responses on WhatsApp and phone whenever you need us.': (
        'ردود سريعة عبر واتساب والهاتف متى احتجت إلينا.',
        'Réponses rapides sur WhatsApp et téléphone quand vous en avez besoin.',
    ),
    'Worldwide destinations': ('وجهات حول العالم', 'Destinations mondiales'),
    'Beaches, cities, honeymoons & group tours across the globe.': (
        'شواطئ، مدن، شهر عسل، ورحلات جماعية إلى مختلف الوجهات.',
        'Plages, villes, lunes de miel et circuits groupés dans le monde entier.',
    ),
    'Choose Your Trip': ('اختر رحلتك', 'Choisissez votre voyage'),
    'Start Your Vacation Today': ('ابدأ عطلتك اليوم', 'Commencez vos vacances aujourd\'hui'),
    "Looking for your dream vacation destination but don't know where to start? With the help of experienced and knowledgeable travel agents, you can plan the trip of a lifetime with ease.": (
        'تبحث عن وجهة أحلامك ولا تعرف من أين تبدأ؟ مع خبراء سما تورز، يمكنك تخطيط رحلة العمر بكل سهولة.',
        'Vous cherchez la destination de vos rêves sans savoir par où commencer ? Avec l\'aide d\'agents expérimentés, planifiez le voyage d\'une vie en toute simplicité.',
    ),
    'View Packages': ('عرض الباقات', 'Voir les forfaits'),
    'Unforgettable experiences': ('تجارب لا تُنسى', 'Expériences inoubliables'),
    'City Walks Tour': ('جولات داخل المدن', 'Visite à pied de la ville'),
    'Discover iconic landmarks and hidden gems with expert local guides.': (
        'اكتشف المعالم الشهيرة والزوايا المخفية مع مرشدين محليين.',
        'Découvrez monuments emblématiques et trésors cachés avec des guides locaux.',
    ),
    'Sunset Boat Cruise': ('رحلة بحرية وقت الغروب', 'Croisière au coucher du soleil'),
    'Relax on the water as the sun sets over breathtaking coastlines.': (
        'استمتع بلحظات هادئة على البحر مع مشهد غروب ساحر.',
        'Détendez-vous sur l\'eau alors que le soleil se couche sur des côtes magnifiques.',
    ),
    'Cultural Experience': ('تجربة ثقافية', 'Expérience culturelle'),
    'Immerse yourself in authentic traditions, cuisine, and heritage.': (
        'تعرّف على التقاليد، المأكولات، والتراث المحلي عن قرب.',
        'Plongez dans les traditions authentiques, la cuisine et le patrimoine.',
    ),
    'Discover your next adventure': ('اكتشف مغامرتك القادمة', 'Découvrez votre prochaine aventure'),
    "Honeymoons, family holidays, or solo journeys — we've got you covered": (
        'شهر عسل، عطلة عائلية، أو رحلة فردية — نحن هنا لنرتّبها لك',
        'Lunes de miel, vacances en famille ou voyages solo — nous vous accompagnons',
    ),
    'Organized Group Tour': ('رحلة جماعية منظمة', 'Circuit groupe organisé'),
    'Join like-minded travelers on curated group journeys.': (
        'انضم إلى مسافرين يشاركونك نفس الشغف في رحلات مخططة بعناية.',
        'Rejoignez des voyageurs partageant les mêmes idées sur des circuits organisés.',
    ),
    'Learn more': ('اعرف المزيد', 'En savoir plus'),
    'Single Customized Trip': ('رحلة خاصة حسب الطلب', 'Voyage personnalisé individuel'),
    'A fully personalized itinerary for your style and budget.': (
        'برنامج سفر مصمم بالكامل حسب ذوقك وميزانيتك.',
        'Un itinéraire entièrement personnalisé selon votre style et budget.',
    ),
    'Get in touch': ('تواصل معنا', 'Nous contacter'),
    'Testimonials': ('آراء عملائنا', 'Témoignages'),
    'Unforgettable Travel Experiences': ('تجارب سفر لا تُنسى', 'Expériences de voyage inoubliables'),
    "Our customers' feedback is essential in building a great reputation and maintaining excellent service. By listening to our customers' needs, we improve our offerings and provide an exceptional travel experience.": (
        'آراء عملائنا هي أساس ثقتنا ونجاحنا. نستمع إلى احتياجاتهم لنطوّر خدماتنا ونقدّم تجربة سفر مريحة ومميزة في كل مرة.',
        'Les retours de nos clients sont essentiels pour notre réputation et notre service. En écoutant leurs besoins, nous améliorons nos offres et offrons une expérience exceptionnelle.',
    ),
    'Previous testimonial': ('الشهادة السابقة', 'Témoignage précédent'),
    'Next testimonial': ('الشهادة التالية', 'Témoignage suivant'),
    'Ready to book your dream vacation?': ('جاهز لحجز عطلة أحلامك؟', 'Prêt à réserver vos vacances de rêve ?'),
    "Contact our team for a detailed quotation — we're here to help.": (
        'تواصل مع فريقنا للحصول على عرض مفصل — نحن هنا لمساعدتك.',
        'Contactez notre équipe pour un devis détaillé — nous sommes là pour vous aider.',
    ),
    'WhatsApp Us': ('راسلنا عبر واتساب', 'Écrivez-nous sur WhatsApp'),
    'About SAMA': ('عن سما', 'À propos de SAMA'),
    'Explore the world with us, one adventure at a time.': (
        'استكشف العالم معنا، مغامرة تلو الأخرى.',
        'Explorez le monde avec nous, une aventure à la fois.',
    ),
    'The Perfect Vacation Come True with Our Travel Agency': (
        'العطلة المثالية تتحقق مع وكالة سفرنا',
        'Des vacances parfaites avec notre agence de voyage',
    ),
    'We are a team of experienced travel experts who specialize in planning and organizing unforgettable travel experiences for our clients with a wide range of travel services, including flight bookings, hotel reservations, and more.': (
        'نحن فريق من خبراء السفر المتمرسين المتخصصين في تخطيط وتنظيم تجارب سفر لا تُنسى، مع مجموعة واسعة من الخدمات.',
        'Nous sommes une équipe d\'experts en voyage spécialisés dans l\'organisation d\'expériences inoubliables : vols, hôtels et plus.',
    ),
    'Get In Touch': ('تواصل معنا', 'Contactez-nous'),
    'Our Services': ('خدماتنا', 'Nos services'),
    'Let us help you plan your next adventure': ('دعنا نساعدك في التخطيط لمغامرتك القادمة', 'Laissez-nous planifier votre prochaine aventure'),
    'Perfect Vacation Come True': ('عطلة مثالية تتحقق', 'Des vacances parfaites'),
    'With our knowledge and expertise in the travel industry, we ensure that all aspects of your trip are tailored to your preferences and budget and make it an experience of a lifetime.': (
        'بمعرفتنا وخبرتنا في صناعة السفر، نضمن تخصيص كل جوانب رحلتك لتفضيلاتك وميزانيتك.',
        'Avec notre expertise, nous adaptons chaque aspect de votre voyage à vos préférences et budget.',
    ),
    'Airline Tickets': ('تذاكر طيران', 'Billets d\'avion'),
    'Ocean Cruises': ('رحلات بحرية', 'Croisières'),
    'Means of Transport': ('وسائل النقل', 'Moyens de transport'),
    'Travel Itineraries': ('برامج السفر', 'Itinéraires de voyage'),
    'Travel Insurance': ('تأمين السفر', 'Assurance voyage'),
    'Local Guide': ('مرشد محلي', 'Guide local'),
    'Exclusive Travel Deals': ('عروض سفر حصرية', 'Offres exclusives'),
    'Book your dream vacation today!': ('احجز عطلتك المثالية اليوم!', 'Réservez vos vacances de rêve aujourd\'hui !'),
    'Book Today': ('احجز اليوم', 'Réserver aujourd\'hui'),
    'Travel Packages': ('باقات السفر', 'Forfaits voyage'),
    'Affordable Travel Packages': ('باقات سفر بأسعار مناسبة', 'Forfaits voyage abordables'),
    'Everyone deserves to experience their dream vacation. Browse, filter, and book instantly via WhatsApp.': (
        'الجميع يستحق عطلتهم المثالية. تصفح، صفِّ وحجز فوراً عبر واتساب.',
        'Chacun mérite ses vacances de rêve. Parcourez, filtrez et réservez instantanément via WhatsApp.',
    ),
    '%(counter)s package found': ('%(counter)s باقة', '%(counter)s forfait trouvé'),
    '%(counter)s packages found': ('%(counter)s باقات', '%(counter)s forfaits trouvés'),
    'No packages match your filters. Try a different country or price range.': (
        'لا توجد باقات تطابق التصفية. جرّب دولة أو ميزانية أخرى.',
        'Aucun forfait ne correspond. Essayez un autre pays ou budget.',
    ),
    'Clear filters': ('مسح التصفية', 'Effacer les filtres'),
    'New packages are coming soon. Contact us for a custom quote.': (
        'باقات جديدة قريباً. تواصل معنا لعرض مخصص.',
        'De nouveaux forfaits arrivent bientôt. Contactez-nous pour un devis sur mesure.',
    ),
    'Browse visa requirement documents by country. Click any card to view or download the PDF.': (
        'تصفح مستندات متطلبات التأشيرة حسب الدولة. انقر على أي بطاقة لفتح PDF.',
        'Parcourez les documents visa par pays. Cliquez sur une carte pour ouvrir le PDF.',
    ),
    'View PDF': ('عرض PDF', 'Voir le PDF'),
    'Click to open document': ('انقر لفتح المستند', 'Cliquer pour ouvrir le document'),
    'Need help with your visa application?': ('تحتاج مساعدة في طلب التأشيرة؟', 'Besoin d\'aide pour votre demande de visa ?'),
    'Ask us on WhatsApp': ('اسألنا على واتساب', 'Demandez-nous sur WhatsApp'),
    'Visa documents are being added. Check back soon or contact us for current requirements.': (
        'يتم إضافة مستندات التأشيرة. عد قريباً أو تواصل معنا.',
        'Les documents visa sont en cours d\'ajout. Revenez bientôt ou contactez-nous.',
    ),
    'Phone': ('الهاتف', 'Téléphone'),
    'Office': ('المكتب', 'Bureau'),
    'Write for anything': ('اكتب لأي استفسار', 'Écrivez pour toute demande'),
    'Write to this email for a detailed quotation and information.': (
        'اكتب إلى هذا البريد للحصول على عرض مفصل ومعلومات.',
        'Écrivez à cet e-mail pour un devis détaillé et des informations.',
    ),
    'Message on WhatsApp': ('راسلنا على واتساب', 'Message sur WhatsApp'),
    'Sama Tours office location': ('موقع مكتب سما تورز', 'Emplacement du bureau Sama Tours'),
    'About this package': ('عن هذه الباقة', 'À propos de ce forfait'),
    'Day-by-day itinerary': ('البرنامج يوماً بيوم', 'Itinéraire jour par jour'),
    'Starting price per person': ('السعر الابتدائي للشخص', 'Prix de départ par personne'),
    'Destination': ('الوجهة', 'Destination'),
    'Duration': ('المدة', 'Durée'),
    'Book on WhatsApp': ('احجز على واتساب', 'Réserver sur WhatsApp'),
    'Get a custom quote': ('احصل على عرض مخصص', 'Demander un devis personnalisé'),
    'Get quote': ('عرض سعر', 'Devis'),
    'You may also like': ('قد يعجبك أيضاً', 'Vous aimerez aussi'),
    'Close': ('إغلاق', 'Fermer'),
    'Get a Travel Quote': ('احصل على عرض سفر', 'Demander un devis voyage'),
    "Fill in your trip details — we'll open WhatsApp with your request ready to send.": (
        'أدخل تفاصيل رحلتك — سنفتح واتساب مع طلبك جاهزاً للإرسال.',
        'Remplissez les détails — nous ouvrirons WhatsApp avec votre demande prête à envoyer.',
    ),
    'From': ('من', 'De'),
    'To': ('إلى', 'À'),
    'Select destination': ('اختر الوجهة', 'Choisir la destination'),
    'Travel dates': ('تواريخ السفر', 'Dates de voyage'),
    'Select departure and return': ('اختر المغادرة والعودة', 'Choisir départ et retour'),
    'Adults': ('بالغون', 'Adultes'),
    'Children': ('أطفال', 'Enfants'),
    'Infants': ('رضع', 'Bébés'),
    'Send on WhatsApp': ('أرسل على واتساب', 'Envoyer sur WhatsApp'),
    'Please select your travel dates.': ('يرجى اختيار تواريخ السفر.', 'Veuillez sélectionner vos dates de voyage.'),
    'Please add at least one traveler.': ('يرجى إضافة مسافر واحد على الأقل.', 'Veuillez ajouter au moins un voyageur.'),
    'Hello Sama Tours! I would like a travel quote.': (
        'مرحباً سما تورز! أود الحصول على عرض سفر.',
        'Bonjour Sama Tours ! Je souhaite un devis voyage.',
    ),
    'From:': ('من:', 'De :'),
    'To:': ('إلى:', 'À :'),
    'Travel dates:': ('تواريخ السفر:', 'Dates de voyage :'),
    'Travelers:': ('المسافرون:', 'Voyageurs :'),
    'Thank you!': ('شكراً لكم!', 'Merci !'),
    'adult': ('بالغ', 'adulte'),
    'adults': ('بالغون', 'adultes'),
    'child': ('طفل', 'enfant'),
    'children': ('أطفال', 'enfants'),
    'infant': ('رضيع', 'bébé'),
    'infants': ('رضع', 'bébés'),
    'From $%(amount)s': ('ابتداءً من $%(amount)s', 'À partir de %(amount)s $'),
    "Hello, I'd like to inquire about Sama Tours services.": (
        'مرحباً، أود الاستفسار عن خدمات سما تورز.',
        'Bonjour, je souhaite des informations sur les services Sama Tours.',
    ),
    'Sama Tours, Gallerie Semaan Crossroad, Hazmieh Highway, Hyundai Car Showroom Building, 1st Floor, Hazmieh': (
        'سما تورز، مفترق غاليري سمعان، أوتوستراد الحازمية، مبنى معرض هيونداي، الطابق الأول، الحازمية',
        'Sama Tours, carrefour Galerie Semaan, autoroute Hazmieh, bâtiment Hyundai, 1er étage, Hazmieh',
    ),
    'Sama Tours — Premium travel agency in Lebanon. Explore the world with expert planning, affordable packages, and visa services.': (
        'سما تورز — وكالة سفر متميزة في لبنان. استكشف العالم مع تخطيط خبير وباقات مناسبة وخدمات تأشيرة.',
        'Sama Tours — agence de voyage premium au Liban. Explorez le monde avec planification experte, forfaits abordables et services visa.',
    ),
    'Hello Sama Tours! I would like to book a package.': (
        'مرحباً سما تورز! أود حجز باقة.',
        'Bonjour Sama Tours ! Je souhaite réserver un forfait.',
    ),
    'Package: %(name)s': ('الباقة: %(name)s', 'Forfait : %(name)s'),
    'Destination: %(dest)s': ('الوجهة: %(dest)s', 'Destination : %(dest)s'),
    'Duration: %(duration)s': ('المدة: %(duration)s', 'Durée : %(duration)s'),
    'Price: %(price)s': ('السعر: %(price)s', 'Prix : %(price)s'),
    'Please share availability and payment details. Thank you!': (
        'يرجى مشاركة التوفر وتفاصيل الدفع. شكراً!',
        'Merci de partager les disponibilités et modalités de paiement. Merci !',
    ),
    'Not specified': ('غير محدد', 'Non précisé'),
    '%(count)s adult': ('%(count)s بالغ', '%(count)s adulte'),
    '%(count)s adults': ('%(count)s بالغون', '%(count)s adultes'),
    '%(count)s child': ('%(count)s طفل', '%(count)s enfant'),
    '%(count)s children': ('%(count)s أطفال', '%(count)s enfants'),
    '%(count)s infant': ('%(count)s رضيع', '%(count)s bébé'),
    '%(count)s infants': ('%(count)s رضع', '%(count)s bébés'),
    'Beach vacation deals': ('عروض عطلات الشاطئ', 'Offres vacances plage'),
    'City break packages': ('باقات عطلات المدينة', 'Forfaits city break'),
    'Visa requirements': ('متطلبات التأشيرات', 'Exigences de visa'),
    'Scenic travel destination': ('وجهة سفر خلابة', 'Destination de voyage pittoresque'),
    'Open %(country)s visa requirements PDF': (
        'فتح PDF متطلبات تأشيرة %(country)s',
        'Ouvrir le PDF des exigences visa %(country)s',
    ),
}


def build_po(lang: str, translations: dict) -> polib.POFile:
    po = polib.POFile()
    po.metadata = {
        'Content-Type': 'text/plain; charset=utf-8',
        'Language': lang,
    }
    idx = 0 if lang == 'ar' else 1
    plural = polib.POEntry(
        msgid='%(counter)s package found',
        msgid_plural='%(counter)s packages found',
        msgstr_plural={
            0: translations['%(counter)s package found'][idx],
            1: translations['%(counter)s packages found'][idx],
        },
    )
    po.append(plural)
    skip = {'%(counter)s package found', '%(counter)s packages found'}
    for msgid, pair in translations.items():
        if msgid in skip:
            continue
        po.append(polib.POEntry(msgid=msgid, msgstr=pair[idx]))
    return po


def main():
    for lang in ('ar', 'fr'):
        po = build_po(lang, MESSAGES)
        folder = BASE / lang / 'LC_MESSAGES'
        folder.mkdir(parents=True, exist_ok=True)
        mo_path = folder / 'django.mo'
        po_path = folder / 'django.po'
        po.save(po_path)
        po.save_as_mofile(mo_path)
        print(f'Wrote {mo_path}')


if __name__ == '__main__':
    main()
