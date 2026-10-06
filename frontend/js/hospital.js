'use strict';

onDOMReady(() => {
    redirectIfNotAuthenticated();

    const user = getCurrentUser();
    if (!user) return;

    const navUserEl = document.getElementById('nav-user-name');
    if (navUserEl) navUserEl.textContent = user.full_name || user.email;

    const welcomeEl = document.getElementById('welcome-message');
    if (welcomeEl) {
        welcomeEl.textContent = `${user.full_name || user.hospital_profile?.name || 'Hospital'} Dashboard`;
    }

    loadHospitalDashboard();

    // Socket updates
    window.addEventListener('bloodlink:inventory_updated', () => {
        loadHospitalDashboard();
    });
    window.addEventListener('bloodlink:new_blood_request', () => {
        loadHospitalDashboard();
    });

    async function loadHospitalDashboard() {
        try {
            const inventory = await api.inventory.list();
            const invList = Array.isArray(inventory) ? inventory : [];

            let totalUnits = 0;
            let lowStockCount = 0;
            const lowStockItems = [];

            invList.forEach(item => {
                const units = item.available_units !== undefined ? item.available_units : item.units;
                totalUnits += units;
                if (units < 5) {
                    lowStockCount++;
                    lowStockItems.push(item);
                }
            });

            // Update stats
            const statTotal = document.getElementById('stat-total-inventory');
            if (statTotal) statTotal.innerHTML = `${totalUnits} <small class="text-sm text-muted">units</small>`;

            const statLow = document.getElementById('stat-low-stock');
            if (statLow) statLow.textContent = lowStockCount;

            // Overview table on dashboard
            const overviewTbody = document.getElementById('inventory-overview-tbody');
            if (overviewTbody) {
                if (invList.length === 0) {
                    overviewTbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">No inventory added yet.</td></tr>';
                } else {
                    let html = '';
                    invList.forEach(item => {
                        const units = item.available_units !== undefined ? item.available_units : item.units;
                        const statusBadge = units < 3 ? '<span class="badge badge-danger">Critical</span>' : 
                                            (units < 5 ? '<span class="badge badge-warning">Low</span>' : '<span class="badge badge-success">Good</span>');
                        html += `
                            <tr>
                                <td><span class="badge badge-blood">${escapeHtml(item.blood_group)}</span></td>
                                <td>${escapeHtml(item.component || 'Whole Blood')}</td>
                                <td><strong>${units}</strong></td>
                                <td>${statusBadge}</td>
                            </tr>
                        `;
                    });
                    overviewTbody.innerHTML = html;
                }
            }

            // Low stock alerts list
            const lowStockList = document.getElementById('low-stock-list');
            if (lowStockList) {
                if (lowStockItems.length === 0) {
                    lowStockList.innerHTML = '<li class="text-success text-center py-2">✓ All blood groups adequately stocked.</li>';
                } else {
                    let html = '';
                    lowStockItems.forEach(item => {
                        const units = item.available_units !== undefined ? item.available_units : item.units;
                        html += `
                            <li class="py-2 border-bottom flex-between align-center">
                                <div>
                                    <span class="badge badge-blood">${escapeHtml(item.blood_group)}</span>
                                    <span class="text-sm text-muted ml-1">${escapeHtml(item.component || 'Whole Blood')}</span>
                                </div>
                                <span class="badge badge-danger font-bold">${units} units left</span>
                            </li>
                        `;
                    });
                    lowStockList.innerHTML = html;
                }
            }

            // Full inventory table on hospital-inventory.html
            const fullTbody = document.getElementById('full-inventory-tbody');
            if (fullTbody) {
                if (invList.length === 0) {
                    fullTbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No inventory found. Click "+ Add Stock" to initialize stock.</td></tr>';
                } else {
                    let html = '';
                    invList.forEach(item => {
                        const units = item.available_units !== undefined ? item.available_units : item.units;
                        html += `
                            <tr>
                                <td><span class="badge badge-blood">${escapeHtml(item.blood_group)}</span></td>
                                <td>${escapeHtml(item.component || 'Whole Blood')}</td>
                                <td><strong>${units}</strong></td>
                                <td>${item.reserved_units || 0}</td>
                                <td>${timeAgo(item.last_updated || item.updated_at)}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline btn-adjust-stock" data-bg="${item.blood_group}" data-comp="${item.component}" data-units="${units}">Adjust</button>
                                </td>
                            </tr>
                        `;
                    });
                    fullTbody.innerHTML = html;

                    fullTbody.querySelectorAll('.btn-adjust-stock').forEach(btn => {
                        btn.addEventListener('click', (e) => {
                            const bg = btn.getAttribute('data-bg');
                            const comp = btn.getAttribute('data-comp');
                            const current = parseInt(btn.getAttribute('data-units'), 10);
                            const newUnits = prompt(`Adjust stock for ${bg} (${comp})\nCurrent units: ${current}\nEnter new quantity:`, current);
                            if (newUnits !== null && !isNaN(newUnits) && parseInt(newUnits, 10) >= 0) {
                                updateStock(bg, comp, parseInt(newUnits, 10));
                            }
                        });
                    });
                }
            }

            // Load incoming requests
            loadRecentHospitalRequests();

        } catch (err) {
            console.error('Hospital data loading error:', err);
        }
    }

    async function updateStock(bg, component, units) {
        try {
            await api.inventory.add({
                blood_group: bg,
                component: component,
                available_units: units,
                units: units
            });
            showToast(`Inventory updated: ${bg} set to ${units} units.`, 'success');
            loadHospitalDashboard();
        } catch (err) {
            showToast(err.message || 'Failed to update inventory.', 'error');
        }
    }

    async function loadRecentHospitalRequests() {
        const listEl = document.getElementById('recent-requests-list');
        if (!listEl) return;

        try {
            const requests = await api.requests.list();
            const list = Array.isArray(requests) ? requests : [];

            const statPendingReq = document.getElementById('stat-pending-req');
            if (statPendingReq) {
                statPendingReq.textContent = list.filter(r => r.status === 'PENDING').length;
            }

            if (list.length === 0) {
                listEl.innerHTML = '<li class="text-center text-muted py-2">No incoming requests.</li>';
                return;
            }

            let html = '';
            list.slice(0, 5).forEach(req => {
                html += `
                    <li class="py-2 border-bottom">
                        <div class="flex-between">
                            <strong>#${req.id} - ${escapeHtml(req.blood_group)}</strong>
                            <span class="badge ${getPriorityBadgeClass(req.priority)}">${req.priority}</span>
                        </div>
                        <p class="text-sm text-muted mb-1">${req.units_required || req.units || 1} units required (${escapeHtml(req.city || 'Local')})</p>
                        <a href="request-details.html?id=${req.id}" class="text-xs text-primary">View Request Details →</a>
                    </li>
                `;
            });
            listEl.innerHTML = html;
        } catch (err) {
            listEl.innerHTML = '<li class="text-center text-muted">Unable to load requests.</li>';
        }
    }

    // Modal Handling for Add Stock
    const btnAddInv = document.getElementById('btn-add-inventory') || document.getElementById('btn-quick-add');
    const modal = document.getElementById('inventory-modal');
    const invForm = document.getElementById('inventory-form');

    if (btnAddInv && modal) {
        btnAddInv.addEventListener('click', () => {
            modal.classList.remove('hidden');
        });
    }

    if (modal) {
        modal.querySelectorAll('.close-modal, .btn-cancel').forEach(btn => {
            btn.addEventListener('click', () => {
                modal.classList.add('hidden');
            });
        });
    }

    if (invForm) {
        invForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const bg = document.getElementById('inv_blood_group').value;
            const comp = document.getElementById('inv_component').value;
            const units = parseInt(document.getElementById('inv_units').value, 10);

            if (isNaN(units) || units < 0) {
                showToast('Units must be 0 or greater.', 'error');
                return;
            }

            await updateStock(bg, comp, units);
            if (modal) modal.classList.add('hidden');
            invForm.reset();
        });
    }
});
