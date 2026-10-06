'use strict';

const API_BASE_URL = '/api/v1';

function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

let isRefreshing = false;

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = { ...getAuthHeaders(), ...options.headers };
    
    try {
        let response = await fetch(url, { ...options, headers });

        if (response.status === 401 && localStorage.getItem('refresh_token') && !isRefreshing && !endpoint.includes('/auth/login')) {
            isRefreshing = true;
            try {
                const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('refresh_token')}`
                    }
                });
                
                if (refreshRes.ok) {
                    const data = await refreshRes.json();
                    const newAccessToken = data.data?.access_token || data.access_token;
                    localStorage.setItem('access_token', newAccessToken);
                    
                    headers['Authorization'] = `Bearer ${newAccessToken}`;
                    response = await fetch(url, { ...options, headers });
                } else {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                }
            } finally {
                isRefreshing = false;
            }
        }

        const contentType = response.headers.get('content-type');
        let data = {};
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        }

        if (!response.ok) {
            const errorMsg = (data && data.error && data.error.message) || (data && data.msg) || 'API Request Failed';
            const err = new Error(errorMsg);
            err.status = response.status;
            err.data = data;
            throw err;
        }

        // Return data payload or whole response
        return data.data !== undefined ? data.data : data;
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

const api = {
    auth: {
        login: (email, password) => apiRequest('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
        register: (data) => apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
        getMe: () => apiRequest('/auth/me'),
        logout: () => {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
            window.location.href = 'login.html';
        }
    },
    blood: {
        getGroups: () => apiRequest('/blood/groups'),
        getAvailability: (params = {}) => {
            const cleanParams = {};
            for (const [k, v] of Object.entries(params)) {
                if (v !== undefined && v !== null && v !== '') cleanParams[k] = v;
            }
            const qs = new URLSearchParams(cleanParams).toString();
            return apiRequest(`/blood/availability?${qs}`);
        }
    },
    requests: {
        create: (data) => apiRequest('/requests', { method: 'POST', body: JSON.stringify(data) }),
        list: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return apiRequest(`/requests?${qs}`);
        },
        myRequests: () => apiRequest('/requests/my'),
        get: (id) => apiRequest(`/requests/${id}`),
        update: (id, data) => apiRequest(`/requests/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
        cancel: (id) => apiRequest(`/requests/${id}/cancel`, { method: 'POST' }),
        getMatches: (id) => apiRequest(`/requests/${id}/matches`)
    },
    inventory: {
        list: () => apiRequest('/inventory'),
        add: (data) => apiRequest('/inventory', { method: 'POST', body: JSON.stringify(data) }),
        update: (data) => apiRequest('/inventory', { method: 'PATCH', body: JSON.stringify(data) }),
        audit: () => apiRequest('/inventory/audit')
    },
    donors: {
        list: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return apiRequest(`/donors?${qs}`);
        },
        get: (id) => apiRequest(`/donors/${id}`),
        getProfile: () => apiRequest('/donors/profile'),
        updateProfile: (data) => apiRequest('/donors/profile', { method: 'PATCH', body: JSON.stringify(data) }),
        updateAvailability: (isAvailable) => apiRequest('/donors/availability', { method: 'PATCH', body: JSON.stringify({ is_available: isAvailable }) })
    },
    hospitals: {
        list: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return apiRequest(`/hospitals?${qs}`);
        },
        get: (id) => apiRequest(`/hospitals/${id}`),
        getInventory: (id) => apiRequest(`/hospitals/${id}/inventory`)
    },
    donations: {
        list: () => apiRequest('/donations'),
        create: (data) => apiRequest('/donations', { method: 'POST', body: JSON.stringify(data) })
    },
    notifications: {
        list: (unreadOnly = false) => apiRequest(`/notifications?unread_only=${unreadOnly}`),
        markRead: (id) => apiRequest(`/notifications/${id}/read`, { method: 'PATCH' }),
        markAllRead: () => apiRequest('/notifications/read-all', { method: 'POST' })
    },
    admin: {
        getStatistics: () => apiRequest('/admin/statistics'),
        getUsers: (role = '') => apiRequest(`/admin/users${role ? `?role=${role}` : ''}`),
        getAuditLogs: () => apiRequest('/admin/audit-logs'),
        verifyHospital: (id, status = 'VERIFIED') => apiRequest(`/admin/hospitals/${id}/verify`, { method: 'PATCH', body: JSON.stringify({ verification_status: status }) })
    }
};

window.api = api;
