/**
 * Customer Service - Frontend JavaScript
 * SOA Mini Supermarket Management System
 */

const API_BASE = '';

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'exclamation-circle';
    toast.innerHTML = `<i class="fas fa-${icon}"></i> ${message}`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function getRankBadge(rank) {
    if (!rank) return '<span class="badge badge-info">N/A</span>';
    const rankClasses = {
        'Bronze': 'bronze',
        'Silver': 'silver',
        'Gold': 'gold',
        'Platinum': 'platinum',
        'Diamond': 'diamond'
    };
    const cls = rankClasses[rank.rank_name] || 'info';
    return `<span class="badge badge-${cls}">${rank.rank_name}</span>`;
}

function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
}

// =====================================================
// TAB NAVIGATION
// =====================================================

function openTab(tabName) {
    // Update nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        }
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');

    // Refresh data if needed
    if (tabName === 'customers') {
        loadCustomers();
    } else if (tabName === 'ranks') {
        loadRanks();
    } else if (tabName === 'points') {
        loadCustomerDropdowns();
    }
}

// Initialize tab navigation
document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => openTab(tab.dataset.tab));
});

// =====================================================
// API FUNCTIONS
// =====================================================

async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    const response = await fetch(`${API_BASE}${endpoint}`, options);
    return response.json();
}

// =====================================================
// CUSTOMER FUNCTIONS
// =====================================================

let allCustomers = [];

async function loadCustomers() {
    try {
        const result = await apiRequest('/api/customers?per_page=100');
        if (result.success) {
            allCustomers = result.data;
            renderCustomerTable(allCustomers);
            loadStatistics();
        }
    } catch (error) {
        showToast('Không thể tải danh sách khách hàng', 'error');
    }
}

function renderCustomerTable(customers) {
    const tbody = document.getElementById('customerTableBody');
    const emptyState = document.getElementById('emptyState');

    if (customers.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';

    tbody.innerHTML = customers.map(customer => `
        <tr>
            <td><strong>${customer.customer_code}</strong></td>
            <td>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div class="customer-avatar" style="width: 36px; height: 36px; font-size: 0.8rem;">
                        ${getInitials(customer.full_name)}
                    </div>
                    ${customer.full_name}
                </div>
            </td>
            <td>${customer.phone}</td>
            <td>${customer.email || '-'}</td>
            <td>${getRankBadge(customer.rank)}</td>
            <td><strong style="color: var(--accent);">${formatCurrency(customer.points)}</strong></td>
            <td>${formatCurrency(customer.total_spent)} đ</td>
            <td>
                <div class="actions">
                    <button class="btn btn-secondary btn-icon btn-sm" onclick="viewCustomer(${customer.id})" title="Xem chi tiết">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-primary btn-icon btn-sm" onclick="editCustomer(${customer.id})" title="Sửa">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger btn-icon btn-sm" onclick="deleteCustomer(${customer.id})" title="Xóa">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function loadStatistics() {
    try {
        const result = await apiRequest('/api/statistics/customers');
        if (result.success) {
            document.getElementById('totalCustomers').textContent = result.data.total_customers;
            document.getElementById('totalPoints').textContent = formatCurrency(result.data.total_points_in_system);
            document.getElementById('totalRevenue').textContent = (result.data.total_revenue / 1000000).toFixed(1);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Search functionality
document.getElementById('searchInput').addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allCustomers.filter(c =>
        c.full_name.toLowerCase().includes(query) ||
        c.phone.includes(query) ||
        c.customer_code.toLowerCase().includes(query) ||
        (c.email && c.email.toLowerCase().includes(query))
    );
    renderCustomerTable(filtered);
});

// Add Customer Form
document.getElementById('addCustomerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        full_name: document.getElementById('fullName').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value || null,
        address: document.getElementById('address').value || null,
        date_of_birth: document.getElementById('dateOfBirth').value || null,
        gender: document.getElementById('gender').value
    };

    try {
        const result = await apiRequest('/api/customers', 'POST', data);
        if (result.success) {
            showToast('Thêm khách hàng thành công!');
            e.target.reset();
            openTab('customers');
        } else {
            showToast(result.error || 'Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        showToast('Không thể thêm khách hàng', 'error');
    }
});

// View Customer Detail
async function viewCustomer(id) {
    try {
        const result = await apiRequest(`/api/customers/${id}?include_history=true`);
        if (result.success) {
            const customer = result.data;
            const content = document.getElementById('customerDetailContent');

            content.innerHTML = `
                <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 24px;">
                    <div class="customer-avatar" style="width: 80px; height: 80px; font-size: 2rem;">
                        ${getInitials(customer.full_name)}
                    </div>
                    <div>
                        <h2 style="margin-bottom: 4px;">${customer.full_name}</h2>
                        <p style="color: var(--text-secondary);">${customer.customer_code}</p>
                        ${getRankBadge(customer.rank)}
                    </div>
                </div>
                
                <div class="grid grid-2" style="gap: 16px; margin-bottom: 24px;">
                    <div style="padding: 16px; background: var(--bg-input); border-radius: 12px;">
                        <div style="color: var(--text-muted); font-size: 0.75rem; margin-bottom: 4px;">ĐIỂM TÍCH LŨY</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--accent);">${formatCurrency(customer.points)}</div>
                    </div>
                    <div style="padding: 16px; background: var(--bg-input); border-radius: 12px;">
                        <div style="color: var(--text-muted); font-size: 0.75rem; margin-bottom: 4px;">TỔNG CHI TIÊU</div>
                        <div style="font-size: 1.5rem; font-weight: 700; color: var(--success);">${formatCurrency(customer.total_spent)} đ</div>
                    </div>
                </div>
                
                <div style="margin-bottom: 24px;">
                    <p><i class="fas fa-phone" style="width: 20px; color: var(--primary-light);"></i> ${customer.phone}</p>
                    <p><i class="fas fa-envelope" style="width: 20px; color: var(--primary-light);"></i> ${customer.email || '-'}</p>
                    <p><i class="fas fa-map-marker-alt" style="width: 20px; color: var(--primary-light);"></i> ${customer.address || '-'}</p>
                    <p><i class="fas fa-calendar" style="width: 20px; color: var(--primary-light);"></i> Ngày sinh: ${formatDate(customer.date_of_birth)}</p>
                </div>
                
                <h3 style="margin-bottom: 16px;"><i class="fas fa-history"></i> Lịch sử mua hàng gần đây</h3>
                ${customer.purchase_history && customer.purchase_history.length > 0 ? `
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Mã HĐ</th>
                                    <th>Ngày</th>
                                    <th>Tổng tiền</th>
                                    <th>Điểm</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${customer.purchase_history.slice(0, 5).map(p => `
                                    <tr>
                                        <td>${p.invoice_code}</td>
                                        <td>${formatDate(p.purchase_date)}</td>
                                        <td>${formatCurrency(p.final_amount)} đ</td>
                                        <td style="color: var(--success);">+${p.points_earned}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                ` : '<p style="color: var(--text-muted);">Chưa có lịch sử mua hàng</p>'}
            `;

            document.getElementById('detailModal').classList.add('active');
        }
    } catch (error) {
        showToast('Không thể tải thông tin khách hàng', 'error');
    }
}

function closeDetailModal() {
    document.getElementById('detailModal').classList.remove('active');
}

// Edit Customer
async function editCustomer(id) {
    try {
        const result = await apiRequest(`/api/customers/${id}`);
        if (result.success) {
            const customer = result.data;
            document.getElementById('editCustomerId').value = customer.id;
            document.getElementById('editFullName').value = customer.full_name;
            document.getElementById('editPhone').value = customer.phone;
            document.getElementById('editEmail').value = customer.email || '';
            document.getElementById('editAddress').value = customer.address || '';
            document.getElementById('editModal').classList.add('active');
        }
    } catch (error) {
        showToast('Không thể tải thông tin khách hàng', 'error');
    }
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
}

document.getElementById('editCustomerForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const id = document.getElementById('editCustomerId').value;
    const data = {
        full_name: document.getElementById('editFullName').value,
        phone: document.getElementById('editPhone').value,
        email: document.getElementById('editEmail').value || null,
        address: document.getElementById('editAddress').value || null
    };

    try {
        const result = await apiRequest(`/api/customers/${id}`, 'PUT', data);
        if (result.success) {
            showToast('Cập nhật thành công!');
            closeEditModal();
            loadCustomers();
        } else {
            showToast(result.error || 'Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        showToast('Không thể cập nhật khách hàng', 'error');
    }
});

// Delete Customer
async function deleteCustomer(id) {
    if (!confirm('Bạn có chắc muốn xóa khách hàng này?')) return;

    try {
        const result = await apiRequest(`/api/customers/${id}`, 'DELETE');
        if (result.success) {
            showToast('Đã xóa khách hàng');
            loadCustomers();
        } else {
            showToast(result.error || 'Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        showToast('Không thể xóa khách hàng', 'error');
    }
}

// =====================================================
// POINTS FUNCTIONS
// =====================================================

async function loadCustomerDropdowns() {
    try {
        const result = await apiRequest('/api/customers?per_page=100');
        if (result.success) {
            const options = result.data.map(c =>
                `<option value="${c.id}" data-points="${c.points}">${c.customer_code} - ${c.full_name} (${c.phone})</option>`
            ).join('');

            document.getElementById('pointsCustomerId').innerHTML = '<option value="">-- Chọn khách hàng --</option>' + options;
            document.getElementById('usePointsCustomerId').innerHTML = '<option value="">-- Chọn khách hàng --</option>' + options;
        }
    } catch (error) {
        console.error('Error loading customer dropdowns:', error);
    }
}

function showCustomerPoints() {
    const select = document.getElementById('usePointsCustomerId');
    const option = select.options[select.selectedIndex];
    const points = option.dataset.points || 0;
    document.getElementById('currentPointsDisplay').textContent = formatCurrency(points) + ' điểm';
}

// Add Points Form
document.getElementById('addPointsForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const customerId = document.getElementById('pointsCustomerId').value;
    const data = {
        amount: parseFloat(document.getElementById('purchaseAmount').value),
        invoice_code: document.getElementById('invoiceCode').value || null,
        note: document.getElementById('pointsNote').value || null
    };

    try {
        const result = await apiRequest(`/api/customers/${customerId}/add-points`, 'POST', data);
        if (result.success) {
            showToast(`Đã tích ${result.data.points_earned} điểm cho khách hàng!`);
            e.target.reset();
            loadCustomerDropdowns();
        } else {
            showToast(result.error || 'Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        showToast('Không thể tích điểm', 'error');
    }
});

// Use Points Form
document.getElementById('usePointsForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const customerId = document.getElementById('usePointsCustomerId').value;
    const data = {
        points: parseInt(document.getElementById('pointsToUse').value)
    };

    try {
        const result = await apiRequest(`/api/customers/${customerId}/use-points`, 'POST', data);
        if (result.success) {
            showToast(`Đã sử dụng ${result.data.points_used} điểm, giảm ${formatCurrency(result.data.discount_amount)} đ`);
            e.target.reset();
            document.getElementById('currentPointsDisplay').textContent = '0 điểm';
            loadCustomerDropdowns();
        } else {
            showToast(result.error || 'Có lỗi xảy ra', 'error');
        }
    } catch (error) {
        showToast('Không thể sử dụng điểm', 'error');
    }
});

// =====================================================
// RANKS FUNCTIONS
// =====================================================

async function loadRanks() {
    try {
        const result = await apiRequest('/api/ranks');
        if (result.success) {
            const container = document.getElementById('ranksContainer');
            const icons = ['🥉', '🥈', '🥇', '💎', '👑'];
            const classes = ['bronze', 'silver', 'gold', 'platinum', 'diamond'];

            container.innerHTML = result.data.map((rank, i) => `
                <div class="rank-card ${classes[i] || 'bronze'}">
                    <div class="rank-icon">${icons[i] || '⭐'}</div>
                    <div class="rank-name">${rank.rank_name}</div>
                    <div class="rank-points">${formatCurrency(rank.min_points)}+ điểm</div>
                    <div class="rank-discount">-${rank.discount_percent}%</div>
                </div>
            `).join('');
        }

        // Load statistics
        const statsResult = await apiRequest('/api/statistics/customers');
        if (statsResult.success) {
            const tbody = document.getElementById('rankStatsBody');
            tbody.innerHTML = statsResult.data.rank_statistics.map(stat => `
                <tr>
                    <td>${getRankBadge(stat.rank)}</td>
                    <td><strong>${stat.count}</strong> khách hàng</td>
                    <td>${formatCurrency(stat.rank.min_points)} điểm</td>
                    <td><span class="badge badge-success">-${stat.rank.discount_percent}%</span></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        showToast('Không thể tải thông tin hạng thành viên', 'error');
    }
}

// =====================================================
// INITIALIZATION
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    loadCustomers();
    loadCustomerDropdowns();
});

// Close modals when clicking outside
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
        }
    });
});
