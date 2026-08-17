(function () {
    var today = new Date().toISOString().split('T')[0];
    ['id_from_date', 'id_till_date', 'home-ins-from', 'home-ins-till'].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.setAttribute('min', today);
    });

    var countInput = document.getElementById('id_traveller_count');

    function updateDobFields() {
        if (!countInput) return;
        var count = parseInt(countInput.value, 10) || 1;
        document.querySelectorAll('.traveller-dob').forEach(function (el) {
            var n = parseInt(el.getAttribute('data-traveller'), 10);
            var show = n <= count;
            el.style.display = show ? '' : 'none';
            var input = el.querySelector('input');
            if (input) input.required = show && n === 1 ? true : show;
        });
    }

    if (countInput) {
        countInput.addEventListener('change', updateDobFields);
        updateDobFields();
    }

    var homeForm = document.querySelector('.insurance-home-search');
    if (homeForm) {
        homeForm.addEventListener('submit', function () {
            var dob = document.getElementById('home-ins-dob-hidden');
            if (!dob) return;
            var birth = document.getElementById('home-ins-birth');
            if (birth && birth.value) {
                dob.value = birth.value;
            }
        });
    }

    var quoteForm = document.getElementById('insurance-quote-form');
    var resultsEl = document.getElementById('insurance-results');
    var quoteUrl = quoteForm && quoteForm.getAttribute('data-quote-url');
    var submitBtn = document.getElementById('insurance-quote-submit');
    var detailModal = document.getElementById('insurance-detail-modal');
    var detailBuyBtn = document.getElementById('insurance-detail-buy');
    var lastBuyTrigger = null;
    var i18n = window.insuranceI18n || {};

    function formatMsg(template, vars) {
        if (!template) return '';
        return template.replace(/%\((\w+)\)s/g, function (_, key) {
            return vars[key] !== undefined && vars[key] !== null ? String(vars[key]) : '';
        });
    }

    function scrollToResults() {
        if (!resultsEl) return;
        requestAnimationFrame(function () {
            var top = resultsEl.getBoundingClientRect().top + window.pageYOffset - 24;
            window.scrollTo({ top: top, behavior: 'smooth' });
        });
    }

    function updateQuoteData(qd) {
        var el = document.getElementById('id_quote_data');
        if (el && qd) {
            el.value = JSON.stringify(qd);
        }
        if (qd && qd.traveller_count) {
            var count = parseInt(qd.traveller_count, 10) || 1;
            for (var i = 1; i <= 4; i++) {
                var block = document.getElementById('insurance-traveller-' + i);
                if (block) block.hidden = i > count;
            }
        }
    }

    if (resultsEl && resultsEl.getAttribute('data-scroll-to')) {
        scrollToResults();
        resultsEl.removeAttribute('data-scroll-to');
    }

    function setQuoteLoading(loading) {
        if (!submitBtn) return;
        submitBtn.disabled = loading;
        submitBtn.setAttribute('aria-busy', loading ? 'true' : 'false');
    }

    if (quoteForm && quoteUrl && resultsEl) {
        quoteForm.addEventListener('submit', function (e) {
            e.preventDefault();
            var params = new URLSearchParams(new FormData(quoteForm));
            var loadingText = quoteForm.getAttribute('data-loading-text') || 'Loading…';

            setQuoteLoading(true);
            resultsEl.innerHTML = '<p class="insurance-loading" role="status">' + loadingText + '</p>';
            scrollToResults();

            fetch(quoteUrl + '?' + params.toString(), {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                credentials: 'same-origin',
            })
                .then(function (res) { return res.json(); })
                .then(function (data) {
                    resultsEl.innerHTML = data.html || '';
                    if (data.quote_data) {
                        updateQuoteData(data.quote_data);
                    }
                    var pageUrl = quoteForm.getAttribute('action') + '?' + params.toString();
                    history.pushState({ insuranceQuote: true }, '', pageUrl);
                    scrollToResults();
                })
                .catch(function () {
                    var errMsg = i18n.loadError || 'Unable to load plans. Please try again.';
                    resultsEl.innerHTML = '<div class="insurance-alert insurance-alert-error" role="alert"><p>' + errMsg + '</p></div>';
                    scrollToResults();
                })
                .finally(function () {
                    setQuoteLoading(false);
                });
        });

        var filterTimer = null;
        function refetchIfResults() {
            if (!resultsEl.querySelector('.insurance-results-head')) return;
            clearTimeout(filterTimer);
            filterTimer = setTimeout(function () {
                if (typeof quoteForm.requestSubmit === 'function') {
                    quoteForm.requestSubmit();
                } else {
                    quoteForm.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            }, 450);
        }

        quoteForm.addEventListener('change', function (e) {
            if (e.target.classList && e.target.classList.contains('insurance-plan-filter')) {
                refetchIfResults();
            }
        });

        var planSearch = document.getElementById('ins-filter-q');
        if (planSearch) {
            planSearch.addEventListener('input', refetchIfResults);
        }
    }

    document.addEventListener('click', function (e) {
        if (e.target.id === 'insurance-clear-filters' && quoteForm) {
            e.preventDefault();
            ['tier', 'covid', 'sport', 'currency', 'max_price', 'min_price', 'q'].forEach(function (name) {
                var el = quoteForm.querySelector('[name="' + name + '"]');
                if (el) el.value = '';
            });
            var sortEl = document.getElementById('ins-filter-sort');
            if (sortEl) sortEl.value = 'price_asc';
            if (resultsEl && resultsEl.querySelector('.insurance-results-head')) {
                if (typeof quoteForm.requestSubmit === 'function') {
                    quoteForm.requestSubmit();
                } else {
                    quoteForm.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            }
        }
    });

    function openDetailModal(trigger) {
        if (!detailModal || !trigger) return;

        var title = document.getElementById('insurance-detail-title');
        var summary = document.getElementById('insurance-detail-summary');
        var badge = document.getElementById('insurance-detail-badge');
        var tripEl = document.getElementById('insurance-detail-trip');
        var priceBox = document.getElementById('insurance-detail-price-box');
        var priceValue = document.getElementById('insurance-detail-price-value');
        var priceAlt = document.getElementById('insurance-detail-price-alt');
        var statsEl = document.getElementById('insurance-detail-stats');
        var benefitCountEl = document.getElementById('insurance-detail-benefit-count');
        var benefitsList = document.getElementById('insurance-detail-benefits');

        var planName = trigger.getAttribute('data-plan-name') || '';
        var fullName = trigger.getAttribute('data-plan-full-name') || planName;
        var planBadge = trigger.getAttribute('data-plan-badge') || '';
        var price = trigger.getAttribute('data-price');
        var currency = trigger.getAttribute('data-currency') || 'USD';
        var tripDays = trigger.getAttribute('data-trip-days');
        var coverageDays = trigger.getAttribute('data-coverage-days');
        var deductiblePrice = trigger.getAttribute('data-deductible-price');
        var residence = trigger.getAttribute('data-residence') || '';
        var destination = trigger.getAttribute('data-destination') || '';
        var fromDate = trigger.getAttribute('data-from-date') || '';
        var tillDate = trigger.getAttribute('data-till-date') || '';
        var travellerCount = trigger.getAttribute('data-traveller-count') || '';
        var benefitCount = trigger.getAttribute('data-benefit-count') || '';

        if (title) title.textContent = fullName;
        if (summary) summary.textContent = trigger.getAttribute('data-summary') || '';

        if (badge) {
            if (planBadge) {
                badge.textContent = planBadge;
                badge.hidden = false;
            } else {
                badge.hidden = true;
            }
        }

        if (tripEl) {
            if (residence && destination) {
                var route = document.createElement('span');
                route.className = 'insurance-detail-trip-route';
                route.textContent = residence + ' → ' + destination;

                var sep = document.createElement('span');
                sep.className = 'insurance-detail-trip-sep';
                sep.textContent = '·';

                var dates = document.createElement('span');
                dates.className = 'insurance-detail-trip-dates';
                dates.textContent = fromDate && tillDate ? fromDate + ' → ' + tillDate : '';

                tripEl.innerHTML = '';
                tripEl.appendChild(route);
                if (dates.textContent) {
                    tripEl.appendChild(sep);
                    tripEl.appendChild(dates);
                }
                tripEl.hidden = false;
            } else {
                tripEl.hidden = true;
            }
        }

        if (priceBox && priceValue) {
            if (price) {
                priceValue.textContent = currency + ' $' + parseFloat(price).toFixed(2);
                priceBox.hidden = false;
            } else {
                priceBox.hidden = true;
            }
        }

        if (priceAlt) {
            if (deductiblePrice) {
                priceAlt.textContent = formatMsg(
                    i18n.deductiblePrice || 'Lower premium with deductible: $%(price)s',
                    { price: parseFloat(deductiblePrice).toFixed(2) },
                );
                priceAlt.hidden = false;
            } else {
                priceAlt.hidden = true;
            }
        }

        if (statsEl) {
            statsEl.innerHTML = '';
            var stats = [];
            if (travellerCount) {
                stats.push({ label: i18n.travellers || 'Travellers', value: travellerCount });
            }
            if (tripDays) {
                stats.push({
                    label: i18n.tripLength || 'Trip length',
                    value: formatMsg(i18n.days || '%(count)s days', { count: tripDays }),
                });
            }
            if (coverageDays) {
                stats.push({
                    label: i18n.coverPeriod || 'Cover period',
                    value: formatMsg(i18n.days || '%(count)s days', { count: coverageDays }),
                });
            }
            if (stats.length) {
                stats.forEach(function (stat) {
                    var box = document.createElement('div');
                    box.className = 'insurance-detail-stat';
                    var val = document.createElement('span');
                    val.className = 'insurance-detail-stat-value';
                    val.textContent = stat.value;
                    var lbl = document.createElement('span');
                    lbl.className = 'insurance-detail-stat-label';
                    lbl.textContent = stat.label;
                    box.appendChild(val);
                    box.appendChild(lbl);
                    statsEl.appendChild(box);
                });
                statsEl.hidden = false;
            } else {
                statsEl.hidden = true;
            }
        }

        if (benefitCountEl) {
            if (benefitCount) {
                benefitCountEl.textContent = formatMsg(
                    i18n.benefitsIncluded || '%(count)s benefits included with this plan',
                    { count: benefitCount },
                );
                benefitCountEl.hidden = false;
            } else {
                benefitCountEl.hidden = true;
            }
        }

        if (benefitsList) {
            benefitsList.innerHTML = '';
            var benefits = [];
            try {
                benefits = JSON.parse(trigger.getAttribute('data-benefits') || '[]');
            } catch (err) {
                benefits = [];
            }
            benefits.forEach(function (item) {
                var li = document.createElement('li');
                var text = document.createElement('span');
                text.className = 'insurance-benefit-text';
                text.textContent = item;
                li.appendChild(text);
                benefitsList.appendChild(li);
            });
        }

        lastBuyTrigger = trigger.closest('.insurance-card')
            ? trigger.closest('.insurance-card').querySelector('.js-insurance-buy')
            : null;

        if (detailBuyBtn) {
            var canBuy = lastBuyTrigger && !lastBuyTrigger.disabled;
            detailBuyBtn.hidden = !canBuy;
            detailBuyBtn.disabled = !canBuy;
        }

        detailModal.classList.add('is-open');
        detailModal.setAttribute('aria-hidden', 'false');
        document.documentElement.classList.add('insurance-modal-open');
        document.body.classList.add('insurance-modal-open');
    }

    function closeDetailModal() {
        if (!detailModal) return;
        detailModal.classList.remove('is-open');
        detailModal.setAttribute('aria-hidden', 'true');
        if (!document.getElementById('insurance-purchase-modal') ||
            !document.getElementById('insurance-purchase-modal').classList.contains('is-open')) {
            document.documentElement.classList.remove('insurance-modal-open');
            document.body.classList.remove('insurance-modal-open');
        }
    }

    document.addEventListener('click', function (e) {
        var detailsBtn = e.target.closest('.js-insurance-details');
        if (detailsBtn) {
            e.preventDefault();
            openDetailModal(detailsBtn);
            return;
        }
        if (e.target.closest('[data-close-insurance-detail]')) {
            e.preventDefault();
            closeDetailModal();
        }
    });

    if (detailBuyBtn) {
        detailBuyBtn.addEventListener('click', function () {
            closeDetailModal();
            if (lastBuyTrigger && !lastBuyTrigger.disabled) {
                lastBuyTrigger.click();
            }
        });
    }

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && detailModal && detailModal.classList.contains('is-open')) {
            closeDetailModal();
        }
    });
})();
