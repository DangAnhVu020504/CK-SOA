/**
 * Employee Service - Frontend JavaScript
 */
const API_BASE = '';
let allEmployees = [];
let allRoles = [];
let allShifts = [];

// Utility Functions
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    const icon = type === 'success' ? 'check-circle' : 'times-circle';
    toast.innerHTML = `<i class="fas fa-${icon}"></i> ${message}`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('vi-VN').format(amount);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('vi-VN');
}

function formatTime(timeString) {
    if (!timeString) return '-';
    return timeString.substring(0, 5);
}

function getRoleBadge(role) {
    if (!role) return '';
    const cls = { 'cashier': 'cashier', 'manager': 'manager', 'admin': 'admin' };
    return `<span class="badge badge-${cls[role.role_code] || 'info'}">${role.role_name}</span>`;
}

function getStatusBadge(status) {
    const labels = { 'active': 'Đang làm', 'inactive': 'Đã nghỉ', 'on_leave': 'Nghỉ phép', 'scheduled': 'Đã lên lịch', 'checked_in': 'Đã vào', 'checked_out': 'Đã ra', 'absent': 'Vắng', 'late': 'Đi muộn' };
    return `<span class="badge badge-${status}">${labels[status] || status}</span>`;
}

function getInitials(name) {
    return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
}

// Tab Navigation
function openTab(tabName) {
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`tab-${tabName}`).classList.add('active');

    if (tabName === 'employees') loadEmployees();
    else if (tabName === 'roles') loadRoles();
    else if (tabName === 'schedule') { loadShifts(); loadEmployeeShifts(); }
    else if (tabName === 'add') loadRolesDropdown();
}

document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => openTab(tab.dataset.tab));
});

// API Request
async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = { method, headers: { 'Content-Type': 'application/json' } };
    if (data) options.body = JSON.stringify(data);
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    return response.json();
}

// Load Employees
async function loadEmployees() {
    try {
        const result = await apiRequest('/api/employees?per_page=100');
        if (result.success) {
            allEmployees = result.data;
            renderEmployeeTable(allEmployees);
            loadStatistics();
        }
    } catch (error) {
        showToast('Không thể tải danh sách', 'error');
    }
}

function renderEmployeeTable(employees) {
    const tbody = document.getElementById('employeeTableBody');
    tbody.innerHTML = employees.map(e => `
        <tr>
            <td><strong>${e.employee_code}</strong></td>
            <td><div style="display:flex;align-items:center;gap:10px;"><div class="employee-avatar" style="width:36px;height:36px;font-size:0.8rem;">${getInitials(e.full_name)}</div>${e.full_name}</div></td>
            <td>${e.phone}</td>
            <td>${getRoleBadge(e.role)}</td>
            <td>${getStatusBadge(e.status)}</td>
            <td class="actions">
                <button class="btn btn-primary btn-icon btn-sm" onclick="editEmployee(${e.id})"><i class="fas fa-edit"></i></button>
                <button class="btn btn-danger btn-icon btn-sm" onclick="deleteEmployee(${e.id})"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `).join('');
}

async function loadStatistics() {
    try {
        const result = await apiRequest('/api/statistics/employees');
        if (result.success) {
            document.getElementById('totalEmployees').textContent = result.data.total_employees;
            document.getElementById('activeToday').textContent = result.data.today_attendance?.checked_in || 0;
        }
    } catch (error) { }
}

// Search
document.getElementById('searchInput')?.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const filtered = allEmployees.filter(emp =>
        emp.full_name.toLowerCase().includes(query) ||
        emp.phone.includes(query) ||
        emp.employee_code.toLowerCase().includes(query)
    );
    renderEmployeeTable(filtered);
});

// Add Employee
document.getElementById('addEmployeeForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        full_name: document.getElementById('fullName').value,
        phone: document.getElementById('phone').value,
        email: document.getElementById('email').value || null,
        password: document.getElementById('password').value,
        role_id: parseInt(document.getElementById('roleId').value),
        salary: parseFloat(document.getElementById('salary').value) || 0,
        hire_date: document.getElementById('hireDate').value,
        gender: document.getElementById('gender').value,
        address: document.getElementById('address').value || null
    };
    try {
        const result = await apiRequest('/api/employees', 'POST', data);
        if (result.success) {
            showToast('Thêm nhân viên thành công!');
            e.target.reset();
            openTab('employees');
        } else {
            showToast(result.error || 'Lỗi', 'error');
        }
    } catch (error) {
        showToast('Không thể thêm', 'error');
    }
});

// Edit Employee
async function editEmployee(id) {
    try {
        const result = await apiRequest(`/api/employees/${id}`);
        if (result.success) {
            const emp = result.data;
            document.getElementById('editEmployeeId').value = emp.id;
            document.getElementById('editFullName').value = emp.full_name;
            document.getElementById('editPhone').value = emp.phone;
            document.getElementById('editRoleId').value = emp.role_id;
            document.getElementById('editStatus').value = emp.status;
            await loadRolesDropdown('editRoleId');
            document.getElementById('editRoleId').value = emp.role_id;
            document.getElementById('editModal').classList.add('active');
        }
    } catch (error) {
        showToast('Lỗi', 'error');
    }
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
}

document.getElementById('editEmployeeForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('editEmployeeId').value;
    const data = {
        full_name: document.getElementById('editFullName').value,
        phone: document.getElementById('editPhone').value,
        role_id: parseInt(document.getElementById('editRoleId').value),
        status: document.getElementById('editStatus').value
    };
    try {
        const result = await apiRequest(`/api/employees/${id}`, 'PUT', data);
        if (result.success) {
            showToast('Cập nhật thành công!');
            closeEditModal();
            loadEmployees();
        } else {
            showToast(result.error || 'Lỗi', 'error');
        }
    } catch (error) {
        showToast('Lỗi cập nhật', 'error');
    }
});

// Delete Employee
async function deleteEmployee(id) {
    if (!confirm('Xác nhận xóa nhân viên?')) return;
    try {
        const result = await apiRequest(`/api/employees/${id}`, 'DELETE');
        if (result.success) {
            showToast('Đã xóa');
            loadEmployees();
        } else {
            showToast(result.error || 'Lỗi', 'error');
        }
    } catch (error) {
        showToast('Lỗi xóa', 'error');
    }
}

// Roles
async function loadRoles() {
    try {
        const result = await apiRequest('/api/roles');
        if (result.success) {
            allRoles = result.data;
            const icons = ['💵', '👔', '👑'];
            document.getElementById('rolesContainer').innerHTML = result.data.map((r, i) => `
                <div class="role-card">
                    <div class="role-icon">${icons[i] || '👤'}</div>
                    <div class="role-name">${r.role_name}</div>
                    <div class="role-count">${r.role_code}</div>
                </div>
            `).join('');
        }
    } catch (error) { }
}

async function loadRolesDropdown(selectId = 'roleId') {
    try {
        const result = await apiRequest('/api/roles');
        if (result.success) {
            const options = result.data.map(r => `<option value="${r.id}">${r.role_name}</option>`).join('');
            document.getElementById(selectId).innerHTML = '<option value="">-- Chọn vai trò --</option>' + options;
        }
    } catch (error) { }
}

// Shifts
async function loadShifts() {
    try {
        const result = await apiRequest('/api/shifts');
        if (result.success) {
            allShifts = result.data;
            document.getElementById('shiftsContainer').innerHTML = result.data.map(s => `
                <div class="shift-card">
                    <div class="shift-name">${s.shift_name}</div>
                    <div class="shift-time">${formatTime(s.start_time)} - ${formatTime(s.end_time)}</div>
                </div>
            `).join('');

            // Populate dropdowns
            const shiftOptions = result.data.map(s => `<option value="${s.id}">${s.shift_name} (${formatTime(s.start_time)} - ${formatTime(s.end_time)})</option>`).join('');
            document.getElementById('shiftId').innerHTML = '<option value="">-- Chọn ca --</option>' + shiftOptions;

            const empResult = await apiRequest('/api/employees?per_page=100');
            if (empResult.success) {
                const empOptions = empResult.data.filter(e => e.status === 'active').map(e => `<option value="${e.id}">${e.employee_code} - ${e.full_name}</option>`).join('');
                document.getElementById('shiftEmployeeId').innerHTML = '<option value="">-- Chọn nhân viên --</option>' + empOptions;
            }
        }
    } catch (error) { }
}

// Assign Shift
document.getElementById('assignShiftForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = {
        employee_id: parseInt(document.getElementById('shiftEmployeeId').value),
        shift_id: parseInt(document.getElementById('shiftId').value),
        work_date: document.getElementById('workDate').value
    };
    try {
        const result = await apiRequest('/api/employee-shifts', 'POST', data);
        if (result.success) {
            showToast('Phân công thành công!');
            e.target.reset();
            loadEmployeeShifts();
        } else {
            showToast(result.error || 'Lỗi', 'error');
        }
    } catch (error) {
        showToast('Lỗi phân công', 'error');
    }
});

// Load Employee Shifts
async function loadEmployeeShifts() {
    try {
        const result = await apiRequest('/api/employee-shifts');
        if (result.success) {
            document.getElementById('employeeShiftsBody').innerHTML = result.data.slice(0, 20).map(s => `
                <tr>
                    <td>${s.employee?.full_name || '-'}</td>
                    <td>${s.shift?.shift_name || '-'}</td>
                    <td>${formatDate(s.work_date)}</td>
                    <td>${getStatusBadge(s.status)}</td>
                    <td class="actions">
                        ${s.status === 'scheduled' ? `<button class="btn btn-success btn-sm" onclick="checkIn(${s.id})"><i class="fas fa-sign-in-alt"></i> Vào</button>` : ''}
                        ${s.status === 'checked_in' || s.status === 'late' ? `<button class="btn btn-warning btn-sm" onclick="checkOut(${s.id})"><i class="fas fa-sign-out-alt"></i> Ra</button>` : ''}
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) { }
}

async function checkIn(id) {
    try {
        const result = await apiRequest(`/api/employee-shifts/${id}/check-in`, 'POST');
        if (result.success) {
            showToast('Chấm công vào thành công!');
            loadEmployeeShifts();
        } else {
            showToast(result.error || 'Lỗi', 'error');
        }
    } catch (error) {
        showToast('Lỗi chấm công', 'error');
    }
}

async function checkOut(id) {
    try {
        const result = await apiRequest(`/api/employee-shifts/${id}/check-out`, 'POST');
        if (result.success) {
            showToast('Chấm công ra thành công!');
            loadEmployeeShifts();
        } else {
            showToast(result.error || 'Lỗi', 'error');
        }
    } catch (error) {
        showToast('Lỗi chấm công', 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadEmployees();
    loadRolesDropdown();
});

document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.classList.remove('active');
    });
});
