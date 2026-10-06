'use strict';

onDOMReady(async () => {
    // 1. LOGIN FORM HANDLER
    const loginForm = document.getElementById('login-form') || document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('email')?.value.trim();
            const password = document.getElementById('password')?.value;
            const errorMsg = document.getElementById('error-message');
            const submitBtn = loginForm.querySelector('button[type="submit"]');

            if (errorMsg) errorMsg.classList.add('hidden');

            if (!email || !password) {
                if (errorMsg) {
                    errorMsg.textContent = 'Please enter both email and password.';
                    errorMsg.classList.remove('hidden');
                } else {
                    showToast('Please enter both email and password.', 'error');
                }
                return;
            }

            try {
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Logging in...';
                }

                const res = await api.auth.login(email, password);

                const token = res.access_token || res.token;
                const refreshToken = res.refresh_token;
                const user = res.user;

                if (token && user) {
                    localStorage.setItem('access_token', token);
                    if (refreshToken) localStorage.setItem('refresh_token', refreshToken);
                    localStorage.setItem('user', JSON.stringify(user));

                    showToast(`Welcome back, ${user.full_name || user.email}!`, 'success');

                    const returnUrl = sessionStorage.getItem('redirect_after_login');
                    if (returnUrl) {
                        sessionStorage.removeItem('redirect_after_login');
                        setTimeout(() => {
                            window.location.href = returnUrl;
                        }, 500);
                    } else {
                        setTimeout(() => {
                            redirectToDashboard(user.role);
                        }, 500);
                    }
                } else {
                    throw new Error('Invalid response from server');
                }
            } catch (err) {
                const message = err.data?.error?.message || err.message || 'Login failed. Please check your credentials.';
                if (errorMsg) {
                    errorMsg.textContent = message;
                    errorMsg.classList.remove('hidden');
                } else {
                    showToast(message, 'error');
                }
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Login';
                }
            }
        });
    }

    // 2. REGISTER FORM HANDLER & ROLE TABS
    const registerForm = document.getElementById('register-form') || document.getElementById('registerForm');
    if (registerForm) {
        const roleTabs = document.querySelectorAll('.role-tabs button, .tab-btn');
        const roleInput = document.getElementById('role');
        const donorFields = document.getElementById('donor-fields') || document.getElementById('donorFields');
        const hospitalFields = document.getElementById('hospital-fields') || document.getElementById('hospitalFields');

        function setRole(role) {
            const normalizedRole = (role || 'patient').toLowerCase();
            if (roleInput) roleInput.value = normalizedRole;

            roleTabs.forEach(btn => {
                const btnRole = (btn.getAttribute('data-role') || btn.dataset.role || '').toLowerCase();
                if (btnRole === normalizedRole) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            if (normalizedRole === 'donor') {
                if (donorFields) {
                    donorFields.classList.remove('hidden');
                    donorFields.style.display = 'block';
                }
                if (hospitalFields) {
                    hospitalFields.classList.add('hidden');
                    hospitalFields.style.display = 'none';
                }
            } else if (normalizedRole === 'hospital') {
                if (donorFields) {
                    donorFields.classList.add('hidden');
                    donorFields.style.display = 'none';
                }
                if (hospitalFields) {
                    hospitalFields.classList.remove('hidden');
                    hospitalFields.style.display = 'block';
                }
            } else {
                if (donorFields) {
                    donorFields.classList.add('hidden');
                    donorFields.style.display = 'none';
                }
                if (hospitalFields) {
                    hospitalFields.classList.add('hidden');
                    hospitalFields.style.display = 'none';
                }
            }
        }

        roleTabs.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const role = btn.getAttribute('data-role') || btn.dataset.role;
                if (role) setRole(role);
            });
        });

        // Check URL param for initial role (e.g. register.html?role=donor)
        const urlParams = new URLSearchParams(window.location.search);
        const initialRole = urlParams.get('role') || 'patient';
        setRole(initialRole);

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const errorMsg = document.getElementById('error-message');
            const submitBtn = registerForm.querySelector('button[type="submit"]');

            if (errorMsg) errorMsg.classList.add('hidden');

            const role = (roleInput ? roleInput.value : 'patient').toUpperCase();
            const fullName = document.getElementById('full_name')?.value?.trim() || document.getElementById('name')?.value?.trim();
            const email = document.getElementById('email')?.value.trim();
            const phone = document.getElementById('phone')?.value.trim();
            const password = document.getElementById('password')?.value;
            const confirmPassword = document.getElementById('confirm_password')?.value || document.getElementById('confirmPassword')?.value;

            if (!fullName || !email || !password) {
                const msg = 'Please fill in all required fields.';
                if (errorMsg) {
                    errorMsg.textContent = msg;
                    errorMsg.classList.remove('hidden');
                } else {
                    showToast(msg, 'error');
                }
                return;
            }

            if (confirmPassword && password !== confirmPassword) {
                const msg = 'Passwords do not match.';
                if (errorMsg) {
                    errorMsg.textContent = msg;
                    errorMsg.classList.remove('hidden');
                } else {
                    showToast(msg, 'error');
                }
                return;
            }

            if (password.length < 8) {
                const msg = 'Password must be at least 8 characters long.';
                if (errorMsg) {
                    errorMsg.textContent = msg;
                    errorMsg.classList.remove('hidden');
                } else {
                    showToast(msg, 'error');
                }
                return;
            }

            const payload = {
                role,
                full_name: fullName,
                email,
                phone,
                password
            };

            if (role === 'DONOR') {
                const bg = document.getElementById('blood_group')?.value || document.getElementById('bloodGroup')?.value || 'O+';
                const city = document.getElementById('city_donor')?.value?.trim() || 'Kolkata';
                const area = document.getElementById('area_donor')?.value?.trim() || '';

                payload.donor_data = {
                    blood_group: bg,
                    city: city,
                    area: area
                };
                payload.blood_group = bg;
                payload.city = city;
                payload.area = area;
            } else if (role === 'HOSPITAL') {
                const hospName = fullName;
                const hospType = document.getElementById('org_type')?.value || 'HOSPITAL';
                const addr = document.getElementById('address')?.value?.trim() || '';
                const city = document.getElementById('city_hospital')?.value?.trim() || 'Kolkata';
                const state = document.getElementById('state')?.value?.trim() || 'West Bengal';

                payload.hospital_data = {
                    name: hospName,
                    type: hospType,
                    address: addr,
                    city: city,
                    state: state
                };
                payload.hospital_name = hospName;
                payload.city = city;
                payload.state = state;
            }

            try {
                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Creating Account...';
                }

                await api.auth.register(payload);
                showToast('Registration successful! Please login.', 'success');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1200);
            } catch (err) {
                const message = err.data?.error?.message || err.message || 'Registration failed. Please check your details.';
                if (errorMsg) {
                    errorMsg.textContent = message;
                    errorMsg.classList.remove('hidden');
                } else {
                    showToast(message, 'error');
                }
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Register';
                }
            }
        });
    }

    // 3. Password Visibility Toggle
    document.querySelectorAll('.btn-toggle-password, #toggle-password, .toggle-password').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const input = btn.closest('.password-input-group')?.querySelector('input') || document.getElementById('password');
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    btn.textContent = '🔒';
                } else {
                    input.type = 'password';
                    btn.textContent = '👁️';
                }
            }
        });
    });
});
