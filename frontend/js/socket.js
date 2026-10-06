'use strict';

let socket = null;

function initSocket() {
    if (typeof io === 'undefined') {
        // Try loading CDN socket.io if missing
        const script = document.createElement('script');
        script.src = 'https://cdn.socket.io/4.7.4/socket.io.min.js';
        script.onload = () => setupSocketConnection();
        document.head.appendChild(script);
        return;
    }
    setupSocketConnection();
}

function setupSocketConnection() {
    if (typeof io === 'undefined') return;

    const token = localStorage.getItem('access_token');
    socket = io({
        auth: { token: token },
        transports: ['websocket', 'polling']
    });

    socket.on('connect', () => {
        console.log('⚡ Connected to BloodLink real-time server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from real-time server');
    });

    socket.on('inventory_updated', (data) => {
        console.log('Real-time inventory update:', data);
        window.dispatchEvent(new CustomEvent('bloodlink:inventory_updated', { detail: data }));
        document.dispatchEvent(new CustomEvent('inventoryUpdate', { detail: data }));
    });

    socket.on('new_blood_request', (data) => {
        console.log('Real-time new blood request:', data);
        showToast(`🚨 New Request: ${data.blood_group} urgently required (${data.city || 'Nearby'})`, 'warning');
        window.dispatchEvent(new CustomEvent('bloodlink:new_blood_request', { detail: data }));
        document.dispatchEvent(new CustomEvent('newRequest', { detail: data }));
    });

    socket.on('donor_match_found', (data) => {
        showToast('🎯 You have a new matching blood request!', 'info');
        window.dispatchEvent(new CustomEvent('bloodlink:donor_match_found', { detail: data }));
    });

    socket.on('request_status_changed', (data) => {
        console.log('Real-time request status change:', data);
        showToast(`Request #${data.id || data.request_id} status updated to: ${data.status}`, 'info');
        window.dispatchEvent(new CustomEvent('bloodlink:request_status_changed', { detail: data }));
        document.dispatchEvent(new CustomEvent('requestUpdate', { detail: data }));
    });

    socket.on('notification_created', (data) => {
        showToast(`🔔 ${data.title || 'Notification'}: ${data.message}`, 'info');
        window.dispatchEvent(new CustomEvent('bloodlink:notification_created', { detail: data }));
        document.dispatchEvent(new CustomEvent('newNotification', { detail: data }));
    });
}

onDOMReady(() => {
    initSocket();
});

window.getSocket = () => socket;
