'use strict';

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
const COMPONENTS = ['Whole Blood', 'Packed Red Blood Cells', 'Plasma', 'Platelets'];
const PRIORITIES = ['NORMAL', 'URGENT', 'EMERGENCY'];
const REQUEST_STATUSES = ['PENDING', 'MATCHING', 'PARTIALLY_FULFILLED', 'FULFILLED', 'CANCELLED'];

// Toast Notification
function showToast(message, type = 'info') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    // Trigger reflow to enable animation
    void toast.offsetWidth;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Loading indicator
function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '<div class="flex-center p-4"><div class="spinner"></div><p class="ml-2">Loading data...</p></div>';
    }
}

function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '';
    }
}

// Modal
function showModal(title, contentHTML, actionsHTML = '') {
    let overlay = document.querySelector('.modal-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h3 class="modal-title"></h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body"></div>
                <div class="modal-footer"></div>
            </div>
        `;
        document.body.appendChild(overlay);
        
        overlay.querySelector('.modal-close').addEventListener('click', closeModal);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) closeModal();
        });
    }

    overlay.querySelector('.modal-title').textContent = title;
    overlay.querySelector('.modal-body').innerHTML = contentHTML;
    const footer = overlay.querySelector('.modal-footer');
    if (actionsHTML) {
        footer.innerHTML = actionsHTML;
        footer.style.display = 'flex';
    } else {
        footer.style.display = 'none';
    }

    overlay.classList.add('active');
}

function closeModal() {
    const overlay = document.querySelector('.modal-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Date Formatting
function formatDate(dateStr) {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function timeAgo(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const seconds = Math.floor((new Date() - date) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + ' years ago';
    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + ' months ago';
    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + ' days ago';
    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + ' hours ago';
    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + ' minutes ago';
    return Math.floor(seconds) + ' seconds ago';
}

function formatDataFreshness(lastUpdated) {
    if (!lastUpdated) return '<span class="badge badge-secondary">Demo Data</span>';
    const date = new Date(lastUpdated);
    const hours = (new Date() - date) / (1000 * 60 * 60);
    const timeAgoStr = timeAgo(lastUpdated);
    
    if (hours > 24) {
        return `<span class="badge badge-warning">⚠️ Outdated (${timeAgoStr}) - Verify with Blood Bank</span>`;
    }
    return `<span class="badge badge-success">✓ Updated ${timeAgoStr}</span>`;
}

// Auth Helpers
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

function getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

function redirectIfNotAuthenticated() {
    if (!isAuthenticated()) {
        try {
            sessionStorage.setItem('redirect_after_login', window.location.href);
        } catch (e) {}
        window.location.href = 'login.html';
    }
}

function redirectToDashboard(role) {
    if (!role) {
        window.location.href = 'index.html';
        return;
    }
    const r = role.toLowerCase();
    if (r === 'hospital') {
        window.location.href = 'hospital-dashboard.html';
    } else if (r === 'donor') {
        window.location.href = 'donor-dashboard.html';
    } else if (r === 'admin') {
        window.location.href = 'admin-dashboard.html';
    } else {
        window.location.href = 'patient-dashboard.html';
    }
}

// Badges
function getPriorityBadgeClass(priority) {
    switch ((priority || '').toUpperCase()) {
        case 'EMERGENCY': 
        case 'CRITICAL': 
            return 'badge-danger';
        case 'URGENT': 
        case 'HIGH': 
            return 'badge-warning';
        default: 
            return 'badge-info';
    }
}

function getStatusBadgeClass(status) {
    switch ((status || '').toUpperCase()) {
        case 'FULFILLED': return 'badge-success';
        case 'PARTIALLY_FULFILLED': return 'badge-warning';
        case 'CANCELLED': return 'badge-danger';
        case 'MATCHING': return 'badge-primary';
        default: return 'badge-info';
    }
}

// Utils
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
         .toString()
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function showEmptyState(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="empty-state text-center p-4">
                <div class="empty-state-icon" style="font-size: 2.5rem; margin-bottom: 0.5rem;">🩸</div>
                <p class="text-muted">${escapeHtml(message)}</p>
            </div>
        `;
    }
}

// DOM Ready Helper
function onDOMReady(fn) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fn);
    } else {
        fn();
    }
}

// Common UI Bindings
onDOMReady(() => {
    // Handle logout buttons
    document.querySelectorAll('[data-action="logout"], .logout-btn, #logout-btn, #sidebar-logout').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    });
    
    // Update user info in UI if present
    const user = getCurrentUser();
    if (user) {
        document.querySelectorAll('.current-user-name, #user-name, #userName, #nav-user-name').forEach(el => {
            el.textContent = user.full_name || user.name || user.email;
        });
        document.querySelectorAll('.current-user-role, #user-role, #userRole').forEach(el => {
            el.textContent = user.role;
        });
        document.querySelectorAll('.auth-only').forEach(el => el.classList.remove('hidden'));
        document.querySelectorAll('.guest-only').forEach(el => el.classList.add('hidden'));
    } else {
        document.querySelectorAll('.auth-only').forEach(el => el.classList.add('hidden'));
        document.querySelectorAll('.guest-only').forEach(el => el.classList.remove('hidden'));
    }
});
