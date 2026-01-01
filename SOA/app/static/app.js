// ===== API Configuration =====
const API_BASE = '/api';

// ===== DOM Elements =====
const tabBtns = document.querySelectorAll('.tab-btn');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const messageDiv = document.getElementById('message');
const authCard = document.querySelector('.auth-card');
const dashboard = document.getElementById('dashboard');

// ===== Tab Navigation =====
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;

        // Update active tab button
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Show corresponding form
        if (tab === 'login') {
            loginForm.classList.add('active');
            registerForm.classList.remove('active');
        } else {
            registerForm.classList.add('active');
            loginForm.classList.remove('active');
        }

        // Clear message
        hideMessage();
    });
});

// ===== Login Form Handler =====
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;

    const btn = loginForm.querySelector('button');
    setLoading(btn, true);

    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('Đăng nhập thành công!', 'success');

            // Save token
            localStorage.setItem('access_token', data.data.access_token);
            localStorage.setItem('refresh_token', data.data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.data.user));

            // Show dashboard
            setTimeout(() => {
                showDashboard(data.data.user);
            }, 1000);
        } else {
            showMessage(data.message || 'Đăng nhập thất bại', 'error');
        }
    } catch (error) {
        showMessage('Lỗi kết nối server', 'error');
        console.error(error);
    } finally {
        setLoading(btn, false);
    }
});

// ===== Register Form Handler =====
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const full_name = document.getElementById('regFullname').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;

    // Validate password match
    if (password !== confirmPassword) {
        showMessage('Mật khẩu xác nhận không khớp', 'error');
        return;
    }

    const btn = registerForm.querySelector('button');
    setLoading(btn, true);

    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password, full_name, phone })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('Đăng ký thành công! Đang chuyển hướng...', 'success');

            // Save token
            localStorage.setItem('access_token', data.data.access_token);
            localStorage.setItem('refresh_token', data.data.refresh_token);
            localStorage.setItem('user', JSON.stringify(data.data.user));

            // Show dashboard
            setTimeout(() => {
                showDashboard(data.data.user);
            }, 1000);
        } else {
            showMessage(data.message || 'Đăng ký thất bại', 'error');
        }
    } catch (error) {
        showMessage('Lỗi kết nối server', 'error');
        console.error(error);
    } finally {
        setLoading(btn, false);
    }
});

// ===== Dashboard Functions =====
function showDashboard(user) {
    authCard.style.display = 'none';
    dashboard.style.display = 'block';

    document.getElementById('userName').textContent = user.full_name || user.username;

    const roleName = user.role ? user.role.name : 'N/A';

    document.getElementById('userDetails').innerHTML = `
        <div class="user-info-item">
            <span class="user-info-label">Username:</span>
            <span class="user-info-value">${user.username}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Email:</span>
            <span class="user-info-value">${user.email}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Họ tên:</span>
            <span class="user-info-value">${user.full_name || 'Chưa cập nhật'}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Số điện thoại:</span>
            <span class="user-info-value">${user.phone || 'Chưa cập nhật'}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Vai trò:</span>
            <span class="user-info-value">${roleName}</span>
        </div>
        <div class="user-info-item">
            <span class="user-info-label">Ngày tạo:</span>
            <span class="user-info-value">${new Date(user.created_at).toLocaleDateString('vi-VN')}</span>
        </div>
    `;
}

// ===== Logout Handler =====
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    dashboard.style.display = 'none';
    authCard.style.display = 'block';

    // Reset forms
    loginForm.reset();
    registerForm.reset();

    showMessage('Đăng xuất thành công', 'success');
});

// ===== Utility Functions =====
function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
}

function hideMessage() {
    messageDiv.className = 'message';
    messageDiv.textContent = '';
}

function setLoading(btn, loading) {
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');

    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline';
        btn.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        btn.disabled = false;
    }
}

// ===== Check for existing login =====
document.addEventListener('DOMContentLoaded', () => {
    const user = localStorage.getItem('user');
    if (user) {
        try {
            showDashboard(JSON.parse(user));
        } catch (e) {
            localStorage.clear();
        }
    }
});
