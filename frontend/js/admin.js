'use strict';

onDOMReady(() => {
    redirectIfNotAuthenticated();

    const user = getCurrentUser();
    if (!user || user.role !== 'ADMIN') {
        showToast('Access denied: Admin privileges required.', 'error');
        setTimeout(() => {
            redirectToDashboard(user ? user.role : '');
        }, 1500);
        return;
    }

    const navUserEl = document.getElementById('nav-user-name');
    if (navUserEl) navUserEl.textContent = `${user.full_name || user.email} (Admin)`;

    loadAdminDashboard();

    async function loadAdminDashboard() {
        try {
            const stats = await api.admin.getStatistics();

            const statUsers = document.getElementById('stat-users') || document.getElementById('total-users');
            if (statUsers) statUsers.textContent = stats.total_users || 0;

            const statDonors = document.getElementById('stat-donors');
            if (statDonors) statDonors.textContent = stats.total_donors || 0;

            const statRequests = document.getElementById('stat-requests') || document.getElementById('total-requests');
            if (statRequests) statRequests.textContent = stats.active_requests || 0;

            const statEmergencies = document.getElementById('stat-emergencies');
            if (statEmergencies) statEmergencies.textContent = stats.emergency_requests || 0;

            // Load recent requests table
            loadAdminRequests();
            // Load user lists
            loadAdminUsers();
            // Load audit logs if on audit page
            loadAdminAuditLogs();

        } catch (err) {
            console.error('Error loading admin statistics:', err);
        }
    }

    let allRequestsData = [];

    async function loadAdminRequests() {
        const tbody = document.getElementById('all-requests-tbody') || document.getElementById('admin-requests-tbody') || document.getElementById('full-requests-tbody');
        if (!tbody) return;

        try {
            const requests = await api.requests.list();
            allRequestsData = Array.isArray(requests) ? requests : [];
            renderAdminRequests(allRequestsData, tbody);
        } catch (err) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Error loading requests.</td></tr>';
        }
    }

    function renderAdminRequests(list, tbody) {
        if (!tbody) return;

        const statusFilter = document.getElementById('req_status')?.value.toUpperCase();
        const priorityFilter = document.getElementById('req_priority')?.value.toUpperCase();

        let filtered = list;
        if (statusFilter) {
            filtered = filtered.filter(r => (r.status || '').toUpperCase() === statusFilter);
        }
        if (priorityFilter) {
            filtered = filtered.filter(r => (r.priority || '').toUpperCase() === priorityFilter);
        }

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No blood requests found.</td></tr>';
            return;
        }

        const isFullTable = !!document.getElementById('all-requests-tbody');
        let html = '';

        if (isFullTable) {
            filtered.forEach(req => {
                html += `
                    <tr>
                        <td><strong>#${req.id}</strong></td>
                        <td>${escapeHtml(req.requester_name || req.hospital_name || `User #${req.requester_id}`)}</td>
                        <td><span class="badge badge-blood">${escapeHtml(req.blood_group)}</span> ${escapeHtml(req.component || 'Whole Blood')}</td>
                        <td><span class="badge ${getPriorityBadgeClass(req.priority)}">${escapeHtml(req.priority)}</span></td>
                        <td><span class="badge ${getStatusBadgeClass(req.status)}">${escapeHtml(req.status)}</span></td>
                        <td>${timeAgo(req.created_at)}</td>
                        <td>
                            <a href="request-details.html?id=${req.id}" class="btn btn-sm btn-outline">Details</a>
                        </td>
                    </tr>
                `;
            });
        } else {
            filtered.slice(0, 8).forEach(req => {
                html += `
                    <tr>
                        <td><strong>#${req.id}</strong></td>
                        <td><span class="badge badge-blood">${escapeHtml(req.blood_group)}</span></td>
                        <td><span class="badge ${getStatusBadgeClass(req.status)}">${escapeHtml(req.status)}</span></td>
                        <td>${timeAgo(req.created_at)}</td>
                    </tr>
                `;
            });
        }

        tbody.innerHTML = html;
    }

    // Filter requests form
    const filterReqForm = document.getElementById('filter-all-reqs-form');
    if (filterReqForm) {
        filterReqForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const tbody = document.getElementById('all-requests-tbody') || document.getElementById('admin-requests-tbody');
            renderAdminRequests(allRequestsData, tbody);
        });
        filterReqForm.addEventListener('change', () => {
            const tbody = document.getElementById('all-requests-tbody') || document.getElementById('admin-requests-tbody');
            renderAdminRequests(allRequestsData, tbody);
        });
    }

    let allUsersData = [];

    async function loadAdminUsers() {
        const userListEl = document.getElementById('recent-users-list');
        const userTableTbody = document.getElementById('users-tbody') || document.getElementById('users-table-tbody');

        try {
            const users = await api.admin.getUsers();
            allUsersData = Array.isArray(users) ? users : [];

            if (userListEl) {
                if (allUsersData.length === 0) {
                    userListEl.innerHTML = '<li class="text-center text-muted">No users found.</li>';
                } else {
                    let html = '';
                    allUsersData.slice(0, 5).forEach(u => {
                        html += `
                            <li class="py-2 border-bottom flex-between align-center">
                                <div>
                                    <strong>${escapeHtml(u.full_name || u.email)}</strong>
                                    <div class="text-xs text-muted">${escapeHtml(u.email)}</div>
                                </div>
                                <span class="badge badge-outline">${escapeHtml(u.role)}</span>
                            </li>
                        `;
                    });
                    userListEl.innerHTML = html;
                }
            }

            renderUsersTable(allUsersData, userTableTbody);

        } catch (err) {
            console.error('Error loading admin users:', err);
        }
    }

    function renderUsersTable(list, tbody) {
        if (!tbody) return;

        const roleFilter = document.getElementById('filter_role')?.value.toUpperCase();
        const searchInput = document.getElementById('search_user')?.value.toLowerCase().trim();

        let filtered = list;
        if (roleFilter) {
            filtered = filtered.filter(u => (u.role || '').toUpperCase() === roleFilter);
        }
        if (searchInput) {
            filtered = filtered.filter(u => 
                (u.full_name && u.full_name.toLowerCase().includes(searchInput)) || 
                (u.email && u.email.toLowerCase().includes(searchInput))
            );
        }

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No users found matching filter.</td></tr>';
            return;
        }

        let html = '';
        filtered.forEach(u => {
            html += `
                <tr>
                    <td><strong>${escapeHtml(u.full_name || 'N/A')}</strong></td>
                    <td>${escapeHtml(u.email)}</td>
                    <td><span class="badge badge-secondary">${escapeHtml(u.role)}</span></td>
                    <td><span class="badge ${u.is_active ? 'badge-success' : 'badge-danger'}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>${formatDate(u.created_at)}</td>
                    <td>
                        <span class="text-xs text-muted">User #${u.id}</span>
                    </td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }

    // Filter users form
    const filterUserForm = document.getElementById('filter-users-form');
    if (filterUserForm) {
        filterUserForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const tbody = document.getElementById('users-tbody') || document.getElementById('users-table-tbody');
            renderUsersTable(allUsersData, tbody);
        });
        filterUserForm.addEventListener('input', () => {
            const tbody = document.getElementById('users-tbody') || document.getElementById('users-table-tbody');
            renderUsersTable(allUsersData, tbody);
        });
    }

    let allAuditData = [];

    async function loadAdminAuditLogs() {
        const tbody = document.getElementById('audit-tbody') || document.getElementById('full-audit-tbody') || document.getElementById('audit-table-container');
        if (!tbody) return;

        try {
            const logs = await api.admin.getAuditLogs();
            allAuditData = Array.isArray(logs) ? logs : [];
            renderAuditLogs(allAuditData, tbody);
        } catch (err) {
            console.error('Error loading audit logs:', err);
        }
    }

    function renderAuditLogs(list, tbody) {
        if (!tbody) return;

        const actionFilter = document.getElementById('audit_action')?.value.toUpperCase();
        const entityFilter = document.getElementById('audit_entity')?.value.toUpperCase();

        let filtered = list;
        if (actionFilter) {
            filtered = filtered.filter(l => (l.action || '').toUpperCase().includes(actionFilter));
        }
        if (entityFilter) {
            filtered = filtered.filter(l => (l.entity_type || '').toUpperCase().includes(entityFilter));
        }

        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No audit logs recorded yet.</td></tr>';
            return;
        }

        let html = '';
        filtered.forEach(log => {
            html += `
                <tr>
                    <td><small class="text-muted">${formatDate(log.created_at)}</small></td>
                    <td>${log.user_id ? `User #${log.user_id}` : 'System'}</td>
                    <td><span class="badge badge-outline font-bold">${escapeHtml(log.action)}</span></td>
                    <td>${escapeHtml(log.entity_type || 'General')} #${log.entity_id || '-'}</td>
                    <td><small class="text-muted">${escapeHtml(log.description || '-')}</small></td>
                    <td><small class="text-muted">${escapeHtml(log.ip_address || '127.0.0.1')}</small></td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    }

    // Filter audit form
    const filterAuditForm = document.getElementById('filter-audit-form');
    if (filterAuditForm) {
        filterAuditForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const tbody = document.getElementById('audit-tbody') || document.getElementById('full-audit-tbody');
            renderAuditLogs(allAuditData, tbody);
        });
        filterAuditForm.addEventListener('change', () => {
            const tbody = document.getElementById('audit-tbody') || document.getElementById('full-audit-tbody');
            renderAuditLogs(allAuditData, tbody);
        });
    }
});
