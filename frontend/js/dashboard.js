'use strict';

onDOMReady(() => {
    redirectIfNotAuthenticated();

    const user = getCurrentUser();
    if (!user) return;

    const welcomeEl = document.getElementById('welcome-message');
    if (welcomeEl) {
        welcomeEl.textContent = `Welcome, ${user.full_name || user.email}`;
    }
    const navUserEl = document.getElementById('nav-user-name');
    if (navUserEl) {
        navUserEl.textContent = user.full_name || user.email;
    }

    loadDashboard();

    // Listen to real-time events
    window.addEventListener('bloodlink:request_status_changed', () => {
        loadDashboard();
    });
    window.addEventListener('bloodlink:new_blood_request', () => {
        loadDashboard();
    });

    async function loadDashboard() {
        try {
            const requests = await api.requests.myRequests();
            const notifs = await api.notifications.list(true);

            let activeCount = 0;
            let fulfilledCount = 0;
            let pendingCount = 0;

            const reqList = Array.isArray(requests) ? requests : [];
            reqList.forEach(r => {
                if (r.status === 'PENDING' || r.status === 'MATCHING') pendingCount++;
                if (r.status === 'FULFILLED') fulfilledCount++;
                if (r.status !== 'CANCELLED' && r.status !== 'FULFILLED') activeCount++;
            });

            // Update stats
            const statActive = document.getElementById('stat-active');
            if (statActive) statActive.textContent = activeCount;

            const statFulfilled = document.getElementById('stat-fulfilled');
            if (statFulfilled) statFulfilled.textContent = fulfilledCount;

            const statPending = document.getElementById('stat-pending');
            if (statPending) statPending.textContent = pendingCount;

            const statNotifs = document.getElementById('stat-notifications');
            if (statNotifs) statNotifs.textContent = Array.isArray(notifs) ? notifs.length : 0;

            // Render requests table
            const tbody = document.getElementById('requests-tbody');
            if (tbody) {
                if (reqList.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">No blood requests created yet. <a href="create-request.html">Create one now</a></td></tr>';
                } else {
                    let html = '';
                    reqList.forEach(req => {
                        html += `
                            <tr>
                                <td><strong>#${req.id}</strong></td>
                                <td><span class="badge badge-blood">${escapeHtml(req.blood_group)}</span> <small class="text-muted">(${req.units_required || req.units || 1} units)</small></td>
                                <td><span class="badge ${getStatusBadgeClass(req.status)}">${escapeHtml(req.status)}</span></td>
                                <td>${timeAgo(req.created_at)}</td>
                                <td>
                                    <a href="request-details.html?id=${req.id}" class="btn btn-sm btn-outline">View Details</a>
                                </td>
                            </tr>
                        `;
                    });
                    tbody.innerHTML = html;
                }
            }

            // Render recent activity list
            const actList = document.getElementById('activity-list');
            if (actList) {
                if (reqList.length === 0) {
                    actList.innerHTML = '<li class="text-muted">No recent activity.</li>';
                } else {
                    let html = '';
                    reqList.slice(0, 5).forEach(req => {
                        html += `
                            <li class="py-2 border-bottom">
                                <strong>Request #${req.id}</strong> (${req.blood_group}) - Status: <span class="badge ${getStatusBadgeClass(req.status)}">${req.status}</span>
                                <small class="text-muted d-block">${formatDate(req.created_at)}</small>
                            </li>
                        `;
                    });
                    actList.innerHTML = html;
                }
            }

        } catch (err) {
            console.error('Error loading patient dashboard:', err);
        }
    }
});
