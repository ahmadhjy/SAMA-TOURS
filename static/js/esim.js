(function () {
    var btn = document.getElementById('esim-load-more');
    if (!btn) return;

    var grid = document.getElementById('esim-results-grid');
    var status = document.getElementById('esim-load-more-status');

    btn.addEventListener('click', function () {
        var params = new URLSearchParams(btn.getAttribute('data-query') || '');
        params.delete('page');
        params.set('page', btn.getAttribute('data-next-page') || '2');

        btn.disabled = true;
        if (status) {
            status.hidden = false;
            status.textContent = btn.getAttribute('data-loading-text') || 'Loading…';
        }

        fetch(btn.getAttribute('data-load-url') + '?' + params.toString(), {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        })
            .then(function (response) {
                return response.json().then(function (data) {
                    if (!response.ok) {
                        throw new Error(data.error || 'Request failed');
                    }
                    return data;
                });
            })
            .then(function (data) {
                if (grid && data.html) {
                    grid.insertAdjacentHTML('beforeend', data.html);
                }
                if (data.has_more) {
                    btn.setAttribute('data-next-page', String(data.next_page));
                    btn.disabled = false;
                } else {
                    var wrap = btn.closest('.esim-load-more-wrap');
                    if (wrap) wrap.remove();
                }
                if (status) status.hidden = true;
            })
            .catch(function (err) {
                btn.disabled = false;
                if (status) {
                    status.textContent = err.message || 'Could not load more plans.';
                }
            });
    });
})();
