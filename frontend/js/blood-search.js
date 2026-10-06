'use strict';

onDOMReady(() => {
    const searchForm = document.getElementById('search-filters-form') || document.getElementById('search-form');
    const resultsContainer = document.getElementById('search-results-container') || document.getElementById('results-container');
    const bloodGroupButtons = document.querySelectorAll('.btn-bg-filter, .blood-group-btn');
    const clearFiltersBtn = document.getElementById('btn-clear-filters') || document.getElementById('clear-filters');
    const resultsCountEl = document.getElementById('results-count');
    const bloodGroupInput = document.getElementById('search_blood_group');
    const cityInput = document.getElementById('search_city') || document.getElementById('city');
    const stateInput = document.getElementById('search_state') || document.getElementById('state');
    const componentSelect = document.getElementById('search_component') || document.getElementById('component');
    const sortSelect = document.getElementById('sort_by');

    let selectedBloodGroup = '';
    let searchResults = [];

    // Parse URL query params if user arrived from homepage quick search
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('blood_group')) {
        selectedBloodGroup = urlParams.get('blood_group');
        if (bloodGroupInput) bloodGroupInput.value = selectedBloodGroup;
    }
    if (urlParams.get('city') && cityInput) {
        cityInput.value = urlParams.get('city');
    }
    if (urlParams.get('state') && stateInput) {
        stateInput.value = urlParams.get('state');
    }
    if (urlParams.get('component') && componentSelect) {
        componentSelect.value = urlParams.get('component');
    }

    // Initialize blood group selector buttons
    bloodGroupButtons.forEach(btn => {
        const bg = btn.getAttribute('data-bg') || btn.dataset.group || btn.textContent.trim();
        if (bg === selectedBloodGroup) {
            btn.classList.add('active');
        }

        btn.addEventListener('click', () => {
            if (selectedBloodGroup === bg) {
                btn.classList.remove('active');
                selectedBloodGroup = '';
            } else {
                bloodGroupButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedBloodGroup = bg;
            }
            if (bloodGroupInput) bloodGroupInput.value = selectedBloodGroup;
            performSearch();
        });
    });

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            performSearch();
        });

        // Debounced search on input
        if (cityInput) cityInput.addEventListener('input', debounce(performSearch, 500));
        if (stateInput) stateInput.addEventListener('input', debounce(performSearch, 500));
        if (componentSelect) componentSelect.addEventListener('change', performSearch);
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            sortAndRender(searchResults);
        });
    }

    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', () => {
            if (searchForm) searchForm.reset();
            bloodGroupButtons.forEach(b => b.classList.remove('active'));
            selectedBloodGroup = '';
            if (bloodGroupInput) bloodGroupInput.value = '';
            performSearch();
        });
    }

    async function performSearch() {
        if (!resultsContainer) return;
        showLoading(resultsContainer.id);

        const params = {
            blood_group: selectedBloodGroup || (bloodGroupInput ? bloodGroupInput.value : ''),
            city: cityInput ? cityInput.value.trim() : '',
            state: stateInput ? stateInput.value.trim() : '',
            component: componentSelect ? componentSelect.value : ''
        };

        try {
            const data = await api.blood.getAvailability(params);
            searchResults = Array.isArray(data) ? data : (data?.availability || []);
            sortAndRender(searchResults);
        } catch (err) {
            console.error('Search error:', err);
            resultsContainer.innerHTML = '<div class="alert alert-danger">Failed to fetch blood availability data.</div>';
        }
    }

    function sortAndRender(items) {
        if (!resultsContainer) return;

        const sortValue = sortSelect ? sortSelect.value : 'units_desc';
        const sorted = [...items].sort((a, b) => {
            if (sortValue === 'units_desc') {
                return (b.units || b.available_units || 0) - (a.units || a.available_units || 0);
            } else if (sortValue === 'freshness') {
                return new Date(b.last_updated || 0) - new Date(a.last_updated || 0);
            }
            return 0;
        });

        if (resultsCountEl) {
            resultsCountEl.textContent = `Showing ${sorted.length} verified results`;
        }

        if (sorted.length === 0) {
            showEmptyState(resultsContainer.id, 'No blood availability records found matching your criteria. You can create an emergency blood request.');
            return;
        }

        let html = '<div class="availability-list">';
        sorted.forEach(item => {
            const units = item.available_units !== undefined ? item.available_units : (item.units !== undefined ? item.units : 0);
            const unitsClass = units >= 5 ? 'text-success' : (units > 0 ? 'text-warning' : 'text-danger');
            const bg = item.blood_group || 'Unknown';
            const bankName = item.blood_bank || item.hospital_name || 'Hospital Blood Bank';
            const address = item.address || item.location || (item.city ? `${item.city}, ${item.state || ''}` : 'Location N/A');
            const category = item.category || 'Blood Bank';
            const component = item.component || 'Whole Blood';
            const phone = item.phone;
            const freshnessHtml = formatDataFreshness(item.last_updated);
            
            let sourceBadge = '<span class="badge badge-info">BloodLink Database</span>';
            if (item.source?.includes('data.gov.in') || item.source_type === 'EXTERNAL') {
                sourceBadge = '<span class="badge badge-primary">🏛️ data.gov.in Directory</span>';
            } else if (item.source_type === 'DONOR') {
                sourceBadge = '<span class="badge badge-success">Active Donor</span>';
            } else if (item.source_type === 'DEMO') {
                sourceBadge = '<span class="badge badge-secondary">Demo Data</span>';
            }

            let phoneHtml = '';
            if (phone) {
                phoneHtml = `<a href="tel:${escapeHtml(phone)}" class="btn btn-sm btn-outline text-success font-bold mt-1">📞 ${escapeHtml(phone)}</a>`;
            }

            html += `
                <div class="card result-card mb-3 p-3">
                    <div class="card-body flex-between align-start wrap gap-3">
                        <div class="result-info" style="flex: 1; min-width: 260px;">
                            <div class="d-flex align-center gap-2 mb-1 flex-wrap">
                                <span class="badge badge-blood font-bold">${escapeHtml(bg)}</span>
                                <h3 class="result-title mb-0">${escapeHtml(bankName)}</h3>
                            </div>
                            <p class="text-muted text-sm mb-2">📍 ${escapeHtml(address)}</p>
                            <div class="result-meta flex-wrap gap-2 align-center">
                                <span class="badge badge-outline">${escapeHtml(category)}</span>
                                <span class="badge badge-outline">${escapeHtml(component)}</span>
                                ${sourceBadge}
                                ${freshnessHtml}
                            </div>
                        </div>
                        <div class="result-actions text-right flex-column align-end">
                            <div class="unit-count ${unitsClass}" style="font-size: 1.75rem; font-weight: 800;">${units} <span class="text-xs font-normal text-muted">units</span></div>
                            <div class="flex-center gap-2 mt-2">
                                ${phoneHtml}
                                <a href="create-request.html?blood_group=${encodeURIComponent(bg)}&city=${encodeURIComponent(item.city || '')}&hospital_name=${encodeURIComponent(bankName)}" class="btn btn-sm btn-primary">Request</a>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        resultsContainer.innerHTML = html;
    }

    // Initial search
    performSearch();
});
