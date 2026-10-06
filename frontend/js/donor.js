'use strict';

onDOMReady(() => {
    redirectIfNotAuthenticated();

    const user = getCurrentUser();
    if (!user) return;

    const navUserEl = document.getElementById('nav-user-name');
    if (navUserEl) navUserEl.textContent = user.full_name || user.email;

    const welcomeEl = document.getElementById('welcome-message');
    if (welcomeEl) welcomeEl.textContent = `Welcome, ${user.full_name || user.email}`;

    // Availability Toggle
    const statusToggle = document.getElementById('status-toggle') || document.getElementById('availability-toggle');
    const statusLabel = document.getElementById('status-label');

    if (statusToggle) {
        statusToggle.addEventListener('change', async (e) => {
            const isAvailable = e.target.checked;
            if (statusLabel) {
                statusLabel.textContent = isAvailable ? 'Available' : 'Unavailable';
                statusLabel.className = isAvailable ? 'text-success font-bold' : 'text-danger font-bold';
            }

            try {
                await api.donors.updateAvailability(isAvailable);
                showToast(`Status updated to ${isAvailable ? 'AVAILABLE' : 'UNAVAILABLE'}.`, 'success');
            } catch (err) {
                showToast(err.message || 'Failed to update availability status.', 'error');
                e.target.checked = !isAvailable;
                if (statusLabel) {
                    statusLabel.textContent = !isAvailable ? 'Available' : 'Unavailable';
                    statusLabel.className = !isAvailable ? 'text-success font-bold' : 'text-danger font-bold';
                }
            }
        });
    }

    loadDonorData();

    // Socket events
    window.addEventListener('bloodlink:new_blood_request', () => {
        loadCompatibleRequests();
    });

    async function loadDonorData() {
        try {
            const meRes = await api.auth.getMe();
            const donorProfile = meRes.donor_profile || meRes;

            const bgEl = document.getElementById('donor-blood-group') || document.getElementById('display-blood-group');
            if (bgEl && donorProfile.blood_group) {
                bgEl.textContent = donorProfile.blood_group;
            }

            if (statusToggle && donorProfile.availability_status) {
                const isAvail = donorProfile.availability_status === 'AVAILABLE';
                statusToggle.checked = isAvail;
                if (statusLabel) {
                    statusLabel.textContent = isAvail ? 'Available' : 'Unavailable';
                    statusLabel.className = isAvail ? 'text-success font-bold' : 'text-danger font-bold';
                }
            }

            // Load donations & stats
            loadDonationsAndStats(donorProfile);
            loadCompatibleRequests(donorProfile.blood_group);
            loadRecentNotifications();

            // Populate profile form if on donor-profile.html
            populateProfileForm(donorProfile, meRes);
        } catch (err) {
            console.error('Error loading donor profile:', err);
        }
    }

    async function loadDonationsAndStats(donorProfile) {
        try {
            const donations = await api.donations.list();
            const statDonations = document.getElementById('stat-donations');
            if (statDonations) {
                statDonations.textContent = Array.isArray(donations) ? donations.length : 0;
            }
        } catch (err) {
            // Ignore error
        }
    }

    let allLoadedRequests = [];

    async function loadCompatibleRequests(bloodGroup) {
        const container = document.getElementById('all-requests-container') || document.getElementById('requests-container') || document.getElementById('compatible-requests-container');
        if (!container) return;

        try {
            const requests = await api.requests.list({ status: 'PENDING' });
            allLoadedRequests = Array.isArray(requests) ? requests : (requests.items || []);

            const statCompatible = document.getElementById('stat-compatible');
            if (statCompatible) statCompatible.textContent = allLoadedRequests.length;

            renderRequests(allLoadedRequests, container);
        } catch (err) {
            console.error('Error loading compatible requests:', err);
            container.innerHTML = '<p class="text-center py-4 text-danger">Failed to load requests.</p>';
        }
    }

    function renderRequests(list, container) {
        if (!container) return;

        const priorityFilter = document.getElementById('filter-priority');
        const selectedPriority = priorityFilter ? priorityFilter.value.toUpperCase() : '';

        const filtered = selectedPriority ? list.filter(r => (r.priority || '').toUpperCase() === selectedPriority) : list;

        if (filtered.length === 0) {
            container.innerHTML = '<div class="col-span-2 text-center py-5"><p class="text-muted">No pending blood requests matching criteria. Thank you for your availability!</p></div>';
            return;
        }

        let html = '';
        filtered.forEach(req => {
            html += `
                <div class="card request-card mb-3 p-3">
                    <div class="flex-between mb-2">
                        <span class="badge badge-blood">${escapeHtml(req.blood_group)}</span>
                        <span class="badge ${getPriorityBadgeClass(req.priority)}">${escapeHtml(req.priority)}</span>
                    </div>
                    <h4 class="mb-1">${req.units_required || req.units || 1} Unit(s) Needed</h4>
                    <p class="text-muted text-sm mb-2">🏥 ${escapeHtml(req.hospital_name || 'Designated Hospital')} (${escapeHtml(req.city || 'Local')})</p>
                    <div class="flex-between align-center mt-3">
                        <small class="text-muted">${timeAgo(req.created_at)}</small>
                        <a href="request-details.html?id=${req.id}" class="btn btn-sm btn-primary">View & Respond</a>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    }

    // Filter and Refresh on donor-requests.html
    const priorityFilter = document.getElementById('filter-priority');
    if (priorityFilter) {
        priorityFilter.addEventListener('change', () => {
            const container = document.getElementById('all-requests-container') || document.getElementById('requests-container') || document.getElementById('compatible-requests-container');
            renderRequests(allLoadedRequests, container);
        });
    }

    const btnRefresh = document.getElementById('btn-refresh-requests');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
            loadCompatibleRequests();
            showToast('Refreshed requests', 'info');
        });
    }

    async function loadRecentNotifications() {
        const notifsList = document.getElementById('recent-notifications');
        if (!notifsList) return;

        try {
            const notifs = await api.notifications.list(false);
            const list = Array.isArray(notifs) ? notifs : (notifs.items || []);

            if (list.length === 0) {
                notifsList.innerHTML = '<li class="text-center text-muted py-2">No new notifications.</li>';
                return;
            }

            let html = '';
            list.slice(0, 4).forEach(n => {
                html += `
                    <li class="notification-item py-2 border-bottom">
                        <strong>${escapeHtml(n.title)}</strong>
                        <p class="text-sm mb-1">${escapeHtml(n.message)}</p>
                        <small class="text-muted">${timeAgo(n.created_at)}</small>
                    </li>
                `;
            });
            notifsList.innerHTML = html;
        } catch (err) {
            notifsList.innerHTML = '<li class="text-center text-muted">Unable to load notifications.</li>';
        }
    }

    function populateProfileForm(donorProfile, user) {
        const form = document.getElementById('donor-profile-form') || document.getElementById('profile-form');
        if (!form) return;

        const fullNameInput = form.querySelector('[name="full_name"], #full_name');
        if (fullNameInput && user.full_name) fullNameInput.value = user.full_name;

        const emailInput = form.querySelector('[name="email"], #email');
        if (emailInput && user.email) emailInput.value = user.email;

        const phoneInput = form.querySelector('[name="phone"], #phone');
        if (phoneInput && user.phone) phoneInput.value = user.phone;

        const bgSelect = form.querySelector('[name="blood_group"], #blood_group');
        if (bgSelect && donorProfile.blood_group) bgSelect.value = donorProfile.blood_group;

        const cityInput = form.querySelector('[name="city"], #city');
        if (cityInput && donorProfile.city) cityInput.value = donorProfile.city;

        const areaInput = form.querySelector('[name="area"], #area');
        if (areaInput && donorProfile.area) areaInput.value = donorProfile.area;

        const isAvailInput = form.querySelector('[name="is_available"], #is_available');
        if (isAvailInput && donorProfile.availability_status) {
            isAvailInput.checked = donorProfile.availability_status === 'AVAILABLE';
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');

            const payload = {
                blood_group: bgSelect ? bgSelect.value : undefined,
                city: cityInput ? cityInput.value.trim() : undefined,
                area: areaInput ? areaInput.value.trim() : undefined,
                is_available: isAvailInput ? isAvailInput.checked : undefined
            };

            try {
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Saving...';
                }

                await api.donors.updateProfile(payload);
                showToast('Donor profile updated successfully!', 'success');
            } catch (err) {
                showToast(err.message || 'Failed to update profile.', 'error');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Save Changes';
                }
            }
        });
    }
});
