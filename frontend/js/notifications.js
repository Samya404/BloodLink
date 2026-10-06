'use strict';

onDOMReady(() => {
    redirectIfNotAuthenticated();

    const user = getCurrentUser();
    if (!user) return;

    const navUserEl = document.getElementById('nav-user-name');
    if (navUserEl) navUserEl.textContent = user.full_name || user.email;

    // Render Dynamic Sidebar based on role
    const sidebar = document.getElementById('dynamic-sidebar');
    if (sidebar) {
        const role = user.role.toLowerCase();
        let homeDashboard = 'patient-dashboard.html';
        if (role === 'hospital') homeDashboard = 'hospital-dashboard.html';
        else if (role === 'donor') homeDashboard = 'donor-dashboard.html';
        else if (role === 'admin') homeDashboard = 'admin-dashboard.html';

        sidebar.innerHTML = `
            <nav class="sidebar-nav">
                <ul>
                    <li><a href="${homeDashboard}">📊 Dashboard</a></li>
                    <li><a href="blood-search.html">🔍 Find Blood</a></li>
                    <li><a href="create-request.html">📝 Blood Request</a></li>
                    <li><a href="notifications.html" class="active">🔔 Notifications</a></li>
                    <li><a href="#" id="sidebar-logout" class="text-danger">🚪 Logout</a></li>
                </ul>
            </nav>
        `;

        const logoutBtn = document.getElementById('sidebar-logout');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                logout();
            });
        }
    }

    const container = document.getElementById('notifications-container');
    const btnMarkAll = document.getElementById('btn-mark-all-read') || document.getElementById('mark-all-read-btn');
    const filterAllBtn = document.getElementById('filter-all-notif');
    const filterUnreadBtn = document.getElementById('filter-unread-notif');

    let unreadOnly = false;

    if (filterAllBtn && filterUnreadBtn) {
        filterAllBtn.addEventListener('click', () => {
            unreadOnly = false;
            filterAllBtn.className = 'btn btn-sm btn-primary';
            filterUnreadBtn.className = 'btn btn-sm btn-outline';
            loadNotifications();
        });

        filterUnreadBtn.addEventListener('click', () => {
            unreadOnly = true;
            filterUnreadBtn.className = 'btn btn-sm btn-primary';
            filterAllBtn.className = 'btn btn-sm btn-outline';
            loadNotifications();
        });
    }

    if (btnMarkAll) {
        btnMarkAll.addEventListener('click', async () => {
            try {
                await api.notifications.markAllRead();
                showToast('All notifications marked as read.', 'success');
                loadNotifications();
            } catch (err) {
                showToast(err.message || 'Failed to mark notifications read.', 'error');
            }
        });
    }

    loadNotifications();

    // Live socket updates
    window.addEventListener('bloodlink:notification_created', () => {
        loadNotifications();
    });

    async function loadNotifications() {
        if (!container) return;
        showLoading(container.id);

        try {
            const notifs = await api.notifications.list(unreadOnly);
            const list = Array.isArray(notifs) ? notifs : (notifs.items || []);

            if (list.length === 0) {
                showEmptyState(container.id, unreadOnly ? 'No unread notifications.' : 'You have no notifications.');
                return;
            }

            let html = '<div class="notifications-wrapper">';
            list.forEach(item => {
                const isReadClass = item.is_read ? 'read bg-white' : 'unread bg-light border-left-primary';
                html += `
                    <div class="card notification-card mb-3 p-3 ${isReadClass}" id="notif-${item.id}">
                        <div class="flex-between align-start">
                            <div>
                                <div class="flex-center gap-2 justify-start mb-1">
                                    <span class="badge ${item.is_read ? 'badge-outline' : 'badge-primary'}">${escapeHtml(item.type || 'Alert')}</span>
                                    <h4 class="mb-0 font-bold">${escapeHtml(item.title)}</h4>
                                </div>
                                <p class="text-muted text-sm mb-1">${escapeHtml(item.message)}</p>
                                <small class="text-muted text-xs">${formatDate(item.created_at)} (${timeAgo(item.created_at)})</small>
                            </div>
                            <div>
                                ${!item.is_read ? `<button class="btn btn-xs btn-outline btn-mark-read" data-id="${item.id}">Mark Read</button>` : '<span class="text-success text-xs">✓ Read</span>'}
                            </div>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;

            container.querySelectorAll('.btn-mark-read').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    const id = btn.getAttribute('data-id');
                    try {
                        await api.notifications.markRead(id);
                        loadNotifications();
                    } catch (err) {
                        showToast(err.message || 'Failed to mark read.', 'error');
                    }
                });
            });

        } catch (err) {
            console.error('Error loading notifications:', err);
            container.innerHTML = '<div class="alert alert-danger">Failed to load notifications.</div>';
        }
    }
});
