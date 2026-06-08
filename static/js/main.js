(function () {
    'use strict';

    // Sticky header shadow
    const header = document.getElementById('site-header');
    if (header) {
        const onScroll = () => {
            header.classList.toggle('scrolled', window.scrollY > 20);
        };
        window.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
    }

    // Mobile navigation
    const navToggle = document.getElementById('nav-toggle');
    const mainNav = document.getElementById('main-nav');
    if (navToggle && mainNav) {
        navToggle.addEventListener('click', () => {
            const open = mainNav.classList.toggle('open');
            navToggle.setAttribute('aria-expanded', open);
        });
        mainNav.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', () => {
                mainNav.classList.remove('open');
                navToggle.setAttribute('aria-expanded', 'false');
            });
        });
    }

    // Testimonial carousel
    const track = document.getElementById('testimonial-track');
    const prevBtn = document.getElementById('testimonial-prev');
    const nextBtn = document.getElementById('testimonial-next');
    const dotsContainer = document.getElementById('testimonial-dots');

    if (track && dotsContainer) {
        const slides = track.querySelectorAll('.testimonial-slide');
        let current = 0;
        let autoplayTimer;

        slides.forEach((_, i) => {
            const dot = document.createElement('button');
            dot.type = 'button';
            dot.className = 'testimonial-dot' + (i === 0 ? ' active' : '');
            dot.setAttribute('aria-label', 'Go to testimonial ' + (i + 1));
            dot.addEventListener('click', () => goTo(i));
            dotsContainer.appendChild(dot);
        });

        const dots = dotsContainer.querySelectorAll('.testimonial-dot');

        function goTo(index) {
            current = (index + slides.length) % slides.length;
            track.style.transform = 'translateX(-' + current * 100 + '%)';
            dots.forEach((d, i) => d.classList.toggle('active', i === current));
        }

        function next() { goTo(current + 1); }
        function prev() { goTo(current - 1); }

        if (prevBtn) prevBtn.addEventListener('click', prev);
        if (nextBtn) nextBtn.addEventListener('click', next);

        function startAutoplay() {
            autoplayTimer = setInterval(next, 6000);
        }
        function stopAutoplay() {
            clearInterval(autoplayTimer);
        }

        const slider = document.getElementById('testimonial-slider');
        if (slider) {
            slider.addEventListener('mouseenter', stopAutoplay);
            slider.addEventListener('mouseleave', startAutoplay);
        }
        startAutoplay();
    }

    // Fade-in on scroll
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        },
        { threshold: 0.1, rootMargin: '0px 0px -40px 0px' }
    );

    document.querySelectorAll('.package-card, .destination-card, .destination-card-tui, .promo-card, .highlight-card, .service-card, .visa-card-link, .why-card').forEach((el) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        if (!window.matchMedia('(max-width: 768px)').matches) {
            el.style.willChange = 'opacity, transform';
        }
        observer.observe(el);
    });

    const style = document.createElement('style');
    style.textContent = '.package-card.visible, .destination-card.visible, .destination-card-tui.visible, .promo-card.visible, .highlight-card.visible, .service-card.visible, .visa-card-link.visible, .why-card.visible { opacity: 1 !important; transform: translateY(0) !important; }';
    document.head.appendChild(style);

    // Quote request modal → WhatsApp
    const quoteModal = document.getElementById('quote-modal');
    const quoteForm = document.getElementById('quote-form');
    const whatsappNumber = document.body.dataset.whatsappNumber || '96176832813';

    function openQuoteModal() {
        if (!quoteModal) return;
        quoteModal.classList.add('open');
        quoteModal.setAttribute('aria-hidden', 'false');
        document.body.classList.add('modal-open');
        const firstInput = quoteForm && quoteForm.querySelector('input:not([type="number"])');
        if (firstInput) firstInput.focus();
    }

    function closeQuoteModal() {
        if (!quoteModal) return;
        quoteModal.classList.remove('open');
        quoteModal.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('modal-open');
    }

    document.querySelectorAll('[data-open-quote]').forEach((btn) => {
        btn.addEventListener('click', openQuoteModal);
    });

    if (quoteModal) {
        quoteModal.querySelectorAll('[data-close-quote]').forEach((el) => {
            el.addEventListener('click', closeQuoteModal);
        });
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && quoteModal.classList.contains('open')) {
                closeQuoteModal();
            }
        });
    }

    const dateInput = document.getElementById('quote-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
    }

    if (quoteForm) {
        quoteForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const from = document.getElementById('quote-from').value.trim();
            const to = document.getElementById('quote-to').value.trim();
            const travelDate = document.getElementById('quote-date').value;
            const adults = parseInt(document.getElementById('quote-adults').value, 10) || 0;
            const children = parseInt(document.getElementById('quote-children').value, 10) || 0;
            const infants = parseInt(document.getElementById('quote-infants').value, 10) || 0;

            if (!from || !to || !travelDate) return;
            if (adults + children + infants < 1) {
                alert('Please add at least one traveler.');
                return;
            }

            const travelers = [];
            if (adults) travelers.push(adults + ' adult' + (adults !== 1 ? 's' : ''));
            if (children) travelers.push(children + ' child' + (children !== 1 ? 'ren' : ''));
            if (infants) travelers.push(infants + ' infant' + (infants !== 1 ? 's' : ''));

            const formattedDate = new Date(travelDate + 'T12:00:00').toLocaleDateString('en-GB', {
                day: 'numeric', month: 'long', year: 'numeric',
            });

            const message =
                'Hello Sama Tours! I would like a travel quote.\n\n' +
                'From: ' + from + '\n' +
                'To: ' + to + '\n' +
                'Travel date: ' + formattedDate + '\n' +
                'Travelers: ' + travelers.join(', ') + '\n\n' +
                'Thank you!';

            const url = 'https://wa.me/' + whatsappNumber + '?text=' + encodeURIComponent(message);
            window.open(url, '_blank', 'noopener,noreferrer');
            closeQuoteModal();
        });
    }
})();
