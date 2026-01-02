/**
 * Mini Supermarket - Simple JavaScript
 */

// ============ ROLE UTILITIES ============
function saveUserSession(userData, token) {
    localStorage.setItem('user', JSON.stringify(userData));
    localStorage.setItem('token', token);
    localStorage.setItem('userRole', userData.role || 'staff');
}

function getUserRole() {
    return localStorage.getItem('userRole') || 'staff';
}

function getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function isAdmin() {
    return getUserRole() === 'admin';
}

function clearSession() {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
}

function redirectBasedOnRole(role) {
    if (role === 'admin') {
        window.location.href = '/dashboard';
    } else {
        window.location.href = '/staff-dashboard';
    }
}

// Tab switching
document.addEventListener('DOMContentLoaded', function () {
    const tabBtns = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            if (this.dataset.tab === 'login') {
                loginForm.classList.add('active');
                registerForm.classList.remove('active');
            } else {
                loginForm.classList.remove('active');
                registerForm.classList.add('active');
            }
        });
    });

    // Login form
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            const submitBtn = this.querySelector('.btn-submit');

            // Show loading state
            submitBtn.classList.add('loading');

            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (data.success) {
                    // Save user session with role
                    saveUserSession(data.data.user, data.data.token);

                    showMessage('Đăng nhập thành công!', 'success');

                    // Redirect based on role
                    setTimeout(() => {
                        redirectBasedOnRole(data.data.user.role);
                    }, 500);
                } else {
                    showMessage(data.message || 'Đăng nhập thất bại', 'error');
                }
            } catch (error) {
                showMessage('Lỗi kết nối server', 'error');
            } finally {
                submitBtn.classList.remove('loading');
            }
        });
    }

    // Register form
    if (registerForm) {
        registerForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const username = document.getElementById('regUsername').value;
            const email = document.getElementById('regEmail').value;
            const full_name = document.getElementById('regFullname').value;
            const password = document.getElementById('regPassword').value;
            const confirmPassword = document.getElementById('regConfirmPassword').value;
            const submitBtn = this.querySelector('.btn-submit');

            if (password !== confirmPassword) {
                showMessage('Mật khẩu không khớp', 'error');
                return;
            }

            submitBtn.classList.add('loading');

            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, full_name, password })
                });

                const data = await response.json();

                if (data.success) {
                    showMessage('Đăng ký thành công! Vui lòng đăng nhập.', 'success');
                    // Switch to login tab
                    document.querySelector('[data-tab="login"]').click();
                } else {
                    showMessage(data.message || 'Đăng ký thất bại', 'error');
                }
            } catch (error) {
                showMessage('Lỗi kết nối server', 'error');
            } finally {
                submitBtn.classList.remove('loading');
            }
        });
    }
});

function showMessage(text, type) {
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        messageDiv.textContent = text;
        messageDiv.className = 'message ' + type;
        messageDiv.style.display = 'block';

        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }
}

// ============ ROLE CHECK FOR PAGES ============
function checkPageAccess(allowedRoles) {
    const userRole = getUserRole();
    if (!allowedRoles.includes(userRole)) {
        // Redirect to appropriate dashboard
        redirectBasedOnRole(userRole);
        return false;
    }
    return true;
}

// Logout function
function logout() {
    clearSession();
    window.location.href = '/';
}
