'use strict';

onDOMReady(() => {
    // 1. CREATE REQUEST FORM
    const createRequestForm = document.getElementById('create-request-form');
    if (createRequestForm) {
        redirectIfNotAuthenticated();

        // Populate from URL params if any
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('blood_group')) {
            const bgEl = document.getElementById('blood_group');
            if (bgEl) bgEl.value = urlParams.get('blood_group');
        }
        if (urlParams.get('hospital_name')) {
            const hospEl = document.getElementById('hospital_name');
            if (hospEl) hospEl.value = urlParams.get('hospital_name');
        }
        if (urlParams.get('city')) {
            const cityEl = document.getElementById('city');
            if (cityEl) cityEl.value = urlParams.get('city');
        }
        if (urlParams.get('priority')) {
            const priorityVal = urlParams.get('priority').toLowerCase();
            const radio = document.querySelector(`input[name="priority"][value="${priorityVal}"]`);
            if (radio) radio.checked = true;
        }

        // Set default required_by to tomorrow if empty
        const requiredByInput = document.getElementById('required_by');
        if (requiredByInput && !requiredByInput.value) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            tomorrow.setMinutes(tomorrow.getMinutes() - tomorrow.getTimezoneOffset());
            requiredByInput.value = tomorrow.toISOString().slice(0, 16);
        }

        createRequestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const submitBtn = document.getElementById('btn-submit-request') || createRequestForm.querySelector('button[type="submit"]');
            const bg = document.getElementById('blood_group').value;
            const component = document.getElementById('component').value;
            const units = parseInt(document.getElementById('units').value, 10);
            const hospitalName = document.getElementById('hospital_name').value.trim();
            const city = document.getElementById('city').value.trim();
            const notes = document.getElementById('notes').value.trim();
            const requiredBy = requiredByInput ? requiredByInput.value : null;

            const priorityRadio = document.querySelector('input[name="priority"]:checked');
            const priority = priorityRadio ? priorityRadio.value.toUpperCase() : 'NORMAL';

            if (!bg) {
                showToast('Blood group is required.', 'error');
                return;
            }
            if (isNaN(units) || units < 1) {
                showToast('Units must be greater than 0.', 'error');
                return;
            }

            const payload = {
                blood_group: bg,
                component: component,
                units: units,
                units_required: units,
                hospital_name: hospitalName,
                city: city,
                priority: priority,
                urgency_level: priority,
                notes: notes,
                required_by: requiredBy ? new Date(requiredBy).toISOString() : null
            };

            try {
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Submitting Request...';
                }

                const newReq = await api.requests.create(payload);
                showToast('Blood request submitted successfully!', 'success');
                setTimeout(() => {
                    window.location.href = `request-details.html?id=${newReq.id}`;
                }, 1000);
            } catch (err) {
                console.error('Create request error:', err);
                showToast(err.message || 'Failed to submit request.', 'error');
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit Request';
                }
            }
        });
    }

    // 2. REQUEST DETAILS VIEW
    const reqIdEl = document.getElementById('req-id');
    if (reqIdEl) {
        const urlParams = new URLSearchParams(window.location.search);
        const reqId = urlParams.get('id');

        if (!reqId) {
            showToast('No request ID provided.', 'error');
            setTimeout(() => {
                window.location.href = 'patient-dashboard.html';
            }, 1500);
            return;
        }

        loadRequestDetails(reqId);
        loadMatches(reqId);

        // Listen for live updates
        window.addEventListener('bloodlink:request_status_changed', (e) => {
            if (e.detail?.id == reqId || e.detail?.request_id == reqId) {
                showToast(`Request status updated: ${e.detail.status}`, 'info');
                loadRequestDetails(reqId);
            }
        });
    }

    async function loadRequestDetails(id) {
        try {
            const req = await api.requests.get(id);

            document.getElementById('req-id').textContent = `Request #${req.id}`;
            
            const statusEl = document.getElementById('req-status');
            if (statusEl) {
                statusEl.textContent = req.status;
                statusEl.className = `badge ${getStatusBadgeClass(req.status)}`;
            }

            const priorityEl = document.getElementById('req-priority');
            if (priorityEl) {
                priorityEl.textContent = req.priority || req.urgency_level || 'NORMAL';
                priorityEl.className = `badge ${getPriorityBadgeClass(req.priority || req.urgency_level)}`;
            }

            const bgEl = document.getElementById('req-blood-group');
            if (bgEl) bgEl.textContent = req.blood_group;

            const compEl = document.getElementById('req-component');
            if (compEl) compEl.textContent = req.component || 'Whole Blood';

            const unitsEl = document.getElementById('req-units');
            if (unitsEl) unitsEl.textContent = `${req.units_required || req.units || 1} Units`;

            const dateEl = document.getElementById('req-date');
            if (dateEl) dateEl.textContent = req.required_by ? formatDate(req.required_by) : 'Urgent / Immediate';

            const hospEl = document.getElementById('req-hospital');
            if (hospEl) hospEl.textContent = req.hospital_name || 'Designated Hospital';

            const cityEl = document.getElementById('req-city');
            if (cityEl) cityEl.textContent = req.city || 'City N/A';

            const notesEl = document.getElementById('req-notes');
            if (notesEl) notesEl.textContent = req.notes || 'No additional notes provided.';

            // Render action buttons
            const actionsEl = document.getElementById('req-actions');
            if (actionsEl) {
                const currentUser = getCurrentUser();
                let actionsHtml = '';

                if (req.status !== 'CANCELLED' && req.status !== 'FULFILLED') {
                    if (currentUser && (currentUser.id === req.requester_id || currentUser.role === 'ADMIN')) {
                        actionsHtml += `<button class="btn btn-outline-danger btn-sm" id="btn-cancel-req">Cancel Request</button>`;
                    }
                    if (currentUser && (currentUser.role === 'HOSPITAL' || currentUser.role === 'ADMIN')) {
                        actionsHtml += `<button class="btn btn-success btn-sm ml-2" id="btn-fulfill-req">Mark as Fulfilled</button>`;
                    }
                }
                actionsEl.innerHTML = actionsHtml;

                const cancelBtn = document.getElementById('btn-cancel-req');
                if (cancelBtn) {
                    cancelBtn.addEventListener('click', async () => {
                        if (confirm('Are you sure you want to cancel this request?')) {
                            try {
                                await api.requests.cancel(id);
                                showToast('Request cancelled.', 'success');
                                loadRequestDetails(id);
                            } catch (err) {
                                showToast(err.message || 'Failed to cancel request.', 'error');
                            }
                        }
                    });
                }

                const fulfillBtn = document.getElementById('btn-fulfill-req');
                if (fulfillBtn) {
                    fulfillBtn.addEventListener('click', async () => {
                        try {
                            await api.requests.update(id, { status: 'FULFILLED' });
                            showToast('Request marked as fulfilled!', 'success');
                            loadRequestDetails(id);
                        } catch (err) {
                            showToast(err.message || 'Failed to update status.', 'error');
                        }
                    });
                }
            }

            // Timeline
            const timelineEl = document.getElementById('req-timeline');
            if (timelineEl) {
                timelineEl.innerHTML = `
                    <div class="timeline-item">
                        <div class="timeline-dot bg-success"></div>
                        <div class="timeline-content">
                            <strong>Created</strong>
                            <p class="text-sm text-muted">${formatDate(req.created_at)}</p>
                        </div>
                    </div>
                    <div class="timeline-item">
                        <div class="timeline-dot ${req.status === 'PENDING' ? 'bg-warning' : 'bg-primary'}"></div>
                        <div class="timeline-content">
                            <strong>Current Status: ${escapeHtml(req.status)}</strong>
                            <p class="text-sm text-muted">${timeAgo(req.updated_at || req.created_at)}</p>
                        </div>
                    </div>
                `;
            }

        } catch (err) {
            console.error('Error fetching request:', err);
            showToast('Failed to load request details.', 'error');
        }
    }

    async function loadMatches(reqId) {
        const tbody = document.getElementById('donors-tbody');
        if (!tbody) return;

        try {
            const matches = await api.requests.getMatches(reqId);
            if (!matches || matches.length === 0) {
                tbody.innerHTML = '<tr><td colspan="2" class="text-center text-muted py-3">No compatible donors found yet. We are notifying nearby donors.</td></tr>';
                return;
            }

            let html = '';
            matches.forEach(m => {
                const score = m.match_score || 0;
                const scoreColor = score >= 80 ? 'text-success font-bold' : (score >= 50 ? 'text-warning font-bold' : 'text-info');
                const donorName = m.donor_name || m.name || `Donor #${m.donor_id}`;
                const bg = m.blood_group || '';
                const locationText = m.location || m.city || 'Nearby Area';
                const distanceText = m.distance_text || (m.distance_km ? `~${m.distance_km} km away` : 'Nearby');
                const phoneHtml = m.phone ? `<a href="tel:${escapeHtml(m.phone)}" class="btn btn-sm btn-outline text-success font-bold mt-1">📞 ${escapeHtml(m.phone)}</a>` : '';

                html += `
                    <tr>
                        <td class="py-3">
                            <div class="d-flex align-center gap-2 mb-1 flex-wrap">
                                <strong>${escapeHtml(donorName)}</strong>
                                ${bg ? `<span class="badge badge-blood font-bold">${escapeHtml(bg)}</span>` : ''}
                            </div>
                            <div class="text-sm text-primary font-semibold">
                                📍 ${escapeHtml(locationText)} <span class="badge badge-outline ml-1 text-xs">${escapeHtml(distanceText)}</span>
                            </div>
                            <div class="text-muted text-xs mt-1">
                                ${escapeHtml(m.reasons || m.reason || 'Compatible Blood Group match')}
                            </div>
                            ${phoneHtml ? `<div class="mt-2">${phoneHtml}</div>` : ''}
                        </td>
                        <td class="py-3 text-right">
                            <div class="badge badge-outline ${scoreColor} mb-1 block">Score: ${score}%</div>
                            <div>
                                <span class="badge badge-sm badge-success">${escapeHtml(m.status || 'Active')}</span>
                            </div>
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        } catch (err) {
            tbody.innerHTML = '<tr><td colspan="2" class="text-center text-muted py-3">Matching info restricted or unavailable.</td></tr>';
        }
    }
});
