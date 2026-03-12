document.addEventListener('DOMContentLoaded', () => {
    // Determine the current page to set active menu and sidebar items
    const path = window.location.pathname;
    const page = path.split("/").pop();

    console.log("Current page:", page);

    // --- GLOBAL API & AUTH UTILITES ---
    const API_BASE_URL = 'http://127.0.0.1:8000/api';

    const setToken = (token) => {
        localStorage.setItem('auth_token', token);
    };

    const getToken = () => {
        return localStorage.getItem('auth_token');
    };

    const clearAuth = () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_role');
    };

    // Helper wrapper for making authorized fetch requests
    const authFetch = async (url, options = {}) => {
        const token = getToken();
        if (!options.headers) options.headers = {};
        options.headers['Content-Type'] = 'application/json';
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }
        return fetch(url, options);
    };

    // Dashboard auth protection
    const isDashboardPage = path.includes('/admin/') || path.includes('dashboard') || path.includes('profile') || path.includes('appointment') || path.includes('history');
    if (isDashboardPage && page !== 'login.html' && page !== 'register.html' && !getToken()) {
        console.warn("Unauthorized! Redirecting to login...");
        window.location.href = path.includes('/admin/') || path.includes('/doctor/') ? '../../pages/login.html' : 'login.html';
        return;
    }
    // --- END AUTH UTILS ---

    // Sidebar menu items based on dashboard type
    const patientMenu = [
        { name: 'Dashboard', icon: 'fas fa-home', link: 'patient_dashboard.html' },
        { name: 'Book Appointment', icon: 'fas fa-calendar-plus', link: 'appointment.html' },
        { name: 'My Appointments', icon: 'fas fa-calendar-check', link: 'my_appointments.html' },
        { name: 'Visit History', icon: 'fas fa-history', link: 'visit_history.html' },
        { name: 'Profile', icon: 'fas fa-user', link: 'profile.html' },
    ];

    const adminMenu = [
        { name: 'Dashboard', icon: 'fas fa-chart-line', link: 'dashboard.html' },
        { name: 'Manage Patients', icon: 'fas fa-users', link: '#' },
        { name: 'Manage Doctors', icon: 'fas fa-user-md', link: '#' },
        { name: 'Appointments', icon: 'fas fa-calendar-alt', link: '#' },
        { name: 'Analytics', icon: 'fas fa-poll', link: 'analytics.html' },
        { name: 'Settings', icon: 'fas fa-cog', link: '#' },
    ];

    const menuContainer = document.getElementById('sidebar-menu');

    if (menuContainer) {
        let menuItems = [];
        if (page.includes('admin') || page.includes('analytics')) {
            menuItems = adminMenu;
        } else {
            menuItems = patientMenu;
        }
        const isSubdir = path.includes('/admin/');

        menuItems.forEach(item => {
            const li = document.createElement('li');
            const a = document.createElement('a');

            // Adjust path based on current directory level
            let finalLink = item.link;
            if (isSubdir && finalLink !== '#') {
                if (finalLink.startsWith('admin/')) {
                    finalLink = finalLink.replace('admin/', '');
                } else {
                    finalLink = '../' + finalLink;
                }
            }
            a.href = finalLink;

            if (path.includes(finalLink) && finalLink !== '#') a.classList.add('active');
            if (page === 'dashboard.html' && finalLink === 'dashboard.html' && isSubdir) a.classList.add('active');

            a.innerHTML = `<i class="${item.icon}"></i> <span>${item.name}</span>`;
            li.appendChild(a);
            menuContainer.appendChild(li);
        });
    }

    // Mobile Sidebar Toggle
    const mobileSidebarToggle = document.getElementById('mobile-sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (mobileSidebarToggle && sidebar) {
        mobileSidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside of it on mobile/tablet
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 992 && sidebar.classList.contains('active') && !sidebar.contains(e.target) && e.target !== mobileSidebarToggle) {
                sidebar.classList.remove('active');
            }
        });
    }

    // Handle Login Simulation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        const roleSelect = document.getElementById('role');
        const registerLink = document.querySelector('.register-link');

        // Initial check on load
        if (roleSelect && registerLink && roleSelect.value === 'admin') {
            registerLink.style.display = 'none';
        }

        if (roleSelect && registerLink) {
            roleSelect.addEventListener('change', (e) => {
                if (e.target.value === 'admin') {
                    registerLink.style.display = 'none';
                } else {
                    registerLink.style.display = 'block';
                }
            });
        }

        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const role = document.getElementById('role').value;
            if (role === 'admin') {
                window.location.href = 'admin/dashboard.html';
            } else if (role === 'doctor') {
                window.location.href = 'doctor/dashboard.html';
            } else {
                window.location.href = 'patient_dashboard.html';
            }
        });
    }
    // --- GLOBAL DATA SYNC ---
    const updateGlobalProfileInfo = async () => {
        if (!isDashboardPage || page === 'login.html' || page === 'register.html') return;
        
        // Initial "Loading..." state to prevent "John Doe" flicker
        const navName = document.getElementById('navUserName');
        const sideName = document.getElementById('sidebarName');
        const sideId = document.getElementById('sidebarId');
        if (navName) navName.textContent = '...';
        if (sideName) sideName.textContent = '...';
        if (sideId) sideId.textContent = 'ID: ...';

        try {
            const profileRes = await authFetch(`${API_BASE_URL}/user/profile`);
            if (profileRes.ok) {
                const profile = await profileRes.json();
                if (navName) navName.textContent = profile.fullName;
                if (sideName) sideName.textContent = profile.fullName;
                if (sideId && profile.id) sideId.textContent = `ID: ${profile.id.substring(0, 8)}...`;
                
                if (page === 'patient_dashboard.html') {
                    const welcomeName = profile.fullName.split(' ')[0];
                    const welcomeMsg = document.getElementById('welcomeMessage');
                    if (welcomeMsg) welcomeMsg.textContent = `Welcome, ${welcomeName}!`;
                }
            }
        } catch (err) {
            console.error("Global profile sync error:", err);
        }
    };
    updateGlobalProfileInfo();

    // --- Appointment Booking Logic ---
    if (page === 'appointment.html' || path.includes('appointment.html')) {
        const deptSelect = document.getElementById('dept');
        const docSelect = document.getElementById('doctor');
        const timeSlotsContainer = document.getElementById('timeSlotsContainer');
        const selectedTimeInput = document.getElementById('selectedTime');
        const appointmentForm = document.getElementById('appointmentForm');

        // Calendar State
        let currentMonth = new Date().getMonth();
        let currentYear = new Date().getFullYear();
        let selectedDate = null;
        let calendarStatus = {};

        const updateCalendar = async () => {
            const doctorId = docSelect.value;
            const calendarGrid = document.getElementById('calendarGrid');
            const monthDisplay = document.getElementById('currentMonthDisplay');
            if (!calendarGrid || !monthDisplay) return;

            const monthStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}`;
            monthDisplay.textContent = new Intl.DateTimeFormat('en-US', { month: 'long', year: 'numeric' }).format(new Date(currentYear, currentMonth));

            // Fetch status if doctor is selected
            if (doctorId) {
                try {
                    const res = await fetch(`${API_BASE_URL}/doctors/${doctorId}/calendar-status?month=${monthStr}`);
                    if (res.ok) calendarStatus = await res.json();
                    else calendarStatus = {};
                } catch (err) {
                    console.error("Error fetching calendar status:", err);
                    calendarStatus = {};
                }
            }

            calendarGrid.innerHTML = '';
            const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
            const firstDay = new Date(currentYear, currentMonth, 1).getDay();

            // Day labels
            ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].forEach(day => {
                const el = document.createElement('div');
                el.className = 'calendar-day-label';
                el.textContent = day;
                calendarGrid.appendChild(el);
            });

            // Empty slots before first day
            for (let i = 0; i < firstDay; i++) {
                const el = document.createElement('div');
                el.className = 'calendar-day disabled';
                calendarGrid.appendChild(el);
            }

            const todayStr = new Date().toISOString().split('T')[0];

            for (let d = 1; d <= daysInMonth; d++) {
                const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
                const el = document.createElement('div');
                el.className = 'calendar-day';
                el.textContent = d;

                if (dateStr < todayStr) {
                    el.classList.add('disabled');
                } else if (!doctorId) {
                    el.classList.add('disabled');
                } else {
                    const status = calendarStatus[dateStr] || 'available';
                    el.classList.add(`status-${status}`);
                    
                    if (status !== 'leave') {
                        el.addEventListener('click', () => {
                            document.querySelectorAll('.calendar-day').forEach(day => day.classList.remove('selected'));
                            el.classList.add('selected');
                            selectedDate = dateStr;
                            document.getElementById('date').value = dateStr;
                            fetchAndRenderSlots(doctorId, dateStr);
                        });
                    }
                }

                if (selectedDate === dateStr) el.classList.add('selected');
                calendarGrid.appendChild(el);
            }
        };

        const fetchAndRenderSlots = async (doctorId, date) => {
            if (!timeSlotsContainer) return;
            timeSlotsContainer.innerHTML = '<div class="loading-slots">Fetching slots...</div>';
            
            try {
                const res = await fetch(`${API_BASE_URL}/appointments/available-slots?doctor_id=${doctorId}&date=${date}`);
                if (!res.ok) throw new Error("Failed to fetch slots");
                const  data = await res.json();
                const slots = data.available_slots || [];
                
                timeSlotsContainer.innerHTML = '';
                if (slots.length === 0) {
                    timeSlotsContainer.innerHTML = '<div style="color:red; grid-column: 1/-1;">No slots available for this date.</div>';
                    return;
                }

                slots.forEach(time => {
                    const div = document.createElement('div');
                    div.className = 'time-slot';
                    div.textContent = time;
                    div.dataset.time = time;
                    div.addEventListener('click', function() {
                        document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                        this.classList.add('selected');
                        if (selectedTimeInput) selectedTimeInput.value = time;
                    });
                    timeSlotsContainer.appendChild(div);
                });
            } catch (err) {
                console.error("Error loading slots:", err);
                timeSlotsContainer.innerHTML = '<div style="color:red;">Error loading slots.</div>';
            }
        };

        // Fetch and setup doctors/depts
        let allDoctors = [];
        const loadDoctorData = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/doctors`);
                if (!res.ok) throw new Error("Failed to fetch doctors");
                allDoctors = await res.json();

                const departments = [...new Set(allDoctors.map(d => d.specialization))].sort();
                deptSelect.innerHTML = '<option value="" disabled selected>Select Department</option>';
                departments.forEach(dept => {
                    const opt = document.createElement('option');
                    opt.value = dept;
                    opt.textContent = dept;
                    deptSelect.appendChild(opt);
                });
            } catch (err) {
                console.error("Error loading doctor data:", err);
            }
        };

        if (deptSelect && docSelect) {
            deptSelect.addEventListener('change', () => {
                const selectedDept = deptSelect.value;
                const filteredDocs = allDoctors.filter(d => d.specialization === selectedDept);
                
                docSelect.innerHTML = '<option value="" disabled selected>Select Doctor</option>';
                filteredDocs.forEach(doc => {
                    const opt = document.createElement('option');
                    opt.value = doc._id;
                    opt.textContent = `${doc.name} (${doc.specialization})`;
                    docSelect.appendChild(opt);
                });

                // Auto-select if only one doctor exists
                if (filteredDocs.length === 1) {
                    docSelect.value = filteredDocs[0]._id;
                    calendarStatus = {};
                    updateCalendar();
                } else {
                    calendarStatus = {};
                    updateCalendar();
                }
            });

            docSelect.addEventListener('change', () => {
                calendarStatus = {};
                updateCalendar();
            });
        }

        document.getElementById('prevMonth')?.addEventListener('click', () => {
            currentMonth--;
            if (currentMonth < 0) { currentMonth = 11; currentYear--; }
            updateCalendar();
        });

        document.getElementById('nextMonth')?.addEventListener('click', () => {
            currentMonth++;
            if (currentMonth > 11) { currentMonth = 0; currentYear++; }
            updateCalendar();
        });

        loadDoctorData();
        updateCalendar();

        if (appointmentForm) {
            appointmentForm.addEventListener('submit', async function (e) {
                e.preventDefault();

                if (!selectedTimeInput.value) {
                    alert("Please select a time slot.");
                    return;
                }

                const btn = this.querySelector('button[type="submit"]');
                const origText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                btn.disabled = true;

                const payload = {
                    department: document.getElementById('dept').value,
                    doctor_id: document.getElementById('doctor').value,
                    appointment_date: document.getElementById('date').value,
                    appointment_time: selectedTimeInput.value
                };

                try {
                    const response = await authFetch(`${API_BASE_URL}/appointments/book`, {
                        method: 'POST',
                        body: JSON.stringify(payload)
                    });
                    
                    if (response.status === 409) {
                        const data = await response.json();
                        alert(data.detail);
                        // Refresh slots to show it's gone
                        fetchAndRenderSlots(payload.doctor_id, payload.appointment_date);
                        btn.innerHTML = origText;
                        btn.disabled = false;
                        return;
                    }

                    if (!response.ok) throw new Error('Booking failed');
                    alert('Appointment booked successfully!');
                    window.location.href = 'my_appointments.html';
                } catch (err) {
                    console.error('Booking error:', err);
                    alert("Failed to book appointment.");
                    btn.innerHTML = origText;
                    btn.disabled = false;
                }
            });
        }
    }

    // --- My Appointments & Cancellation Logic ---
    window.cancelAppointment = async (id) => {
        try {
            const res = await authFetch(`${API_BASE_URL}/appointments/${id}`, { method: 'DELETE' });
            if (res.ok) return true;
            throw new Error("Delete failed");
        } catch (err) {
            console.error("Error cancelling appointment:", err);
            alert("Failed to cancel appointment.");
            return false;
        }
    };

    if (page === 'my_appointments.html' || path.includes('my_appointments.html')) {
        const list = document.getElementById('appointmentsList');
        if (list) {
            const fetchAppointments = async () => {
                try {
                    const res = await authFetch(`${API_BASE_URL}/appointments/user`);
                    if (!res.ok) throw new Error("Fetch failed");
                    const data = await res.json();
                    
                    list.innerHTML = '';
                    if (data.length === 0) {
                        list.innerHTML = '<tr><td colspan="6" style="text-align:center;">No upcoming appointments.</td></tr>';
                        return;
                    }

                    data.forEach(app => {
                        const tr = document.createElement('tr');
                        const statusClass = `status-${app.status.toLowerCase()}`;
                        tr.innerHTML = `
                            <td><strong>${app.doctor_name || 'Doctor'}</strong></td>
                            <td>${app.department}</td>
                            <td>${app.appointment_date}</td>
                            <td>${app.appointment_time}</td>
                            <td><span class="status-badge ${statusClass}">${app.status}</span></td>
                            <td><button class="btn-cancel" onclick="openModal(this, '${app._id}')">Cancel</button></td>
                        `;
                        list.appendChild(tr);
                    });
                } catch (err) {
                    console.error("Error loading appointments:", err);
                    list.innerHTML = '<tr><td colspan="6" style="text-align:center; color:red;">Failed to load data.</td></tr>';
                }
            };
            fetchAppointments();
        }
    }

    // --- Visit History Logic ---
    if (page === 'visit_history.html' || path.includes('visit_history.html')) {
        const list = document.getElementById('historyList');
        if (list) {
            const fetchHistory = async () => {
                try {
                    const res = await authFetch(`${API_BASE_URL}/appointments/history`);
                    if (!res.ok) throw new Error("Fetch failed");
                    const data = await res.json();
                    
                    list.innerHTML = '';
                    if (data.length === 0) {
                        list.innerHTML = '<tr><td colspan="5" style="text-align:center;">No visit history found.</td></tr>';
                        return;
                    }

                    data.forEach(visit => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td><strong>${visit.doctor_name || visit.doctor || 'Doctor'}</strong></td>
                            <td>${visit.department}</td>
                            <td>${visit.appointment_date || visit.date}</td>
                            <td>${visit.appointment_time || visit.time}</td>
                            <td><span class="status-badge status-confirmed">Completed</span></td>
                        `;
                        list.appendChild(tr);
                    });
                } catch (err) {
                    console.error("Error loading history:", err);
                }
            };
            fetchHistory();
        }
    }

    // --- DASHBOARD STATISTICS OVERRIDE ---
    if (page === 'patient_dashboard.html') {
        const fetchDashboardStats = async () => {
            try {
                const res = await authFetch(`${API_BASE_URL}/appointments/user`);
                if (!res.ok) return;
                const appointments = await res.json();
                
                const now = new Date();
                const sorted = appointments.sort((a, b) => new Date(a.appointment_date + ' ' + a.appointment_time) - new Date(b.appointment_date + ' ' + b.appointment_time));
                const upcoming = sorted.find(a => new Date(a.appointment_date + ' ' + a.appointment_time) >= now && a.status !== 'cancelled');
                const past = sorted.filter(a => new Date(a.appointment_date + ' ' + a.appointment_time) < now || a.status === 'completed');

                if (upcoming && document.getElementById('nextApptDate')) {
                    document.getElementById('nextApptDate').textContent = `${upcoming.appointment_date}, ${upcoming.appointment_time}`;
                    const details = document.getElementById('nextApptDetails');
                    if (details) details.textContent = `${upcoming.doctor_name || 'Doctor'} - ${upcoming.department}`;
                }
                if (document.getElementById('pastVisitsCount')) {
                    document.getElementById('pastVisitsCount').textContent = `${past.length} Visits`;
                    const lastVisit = document.getElementById('lastVisitDetails');
                    if (lastVisit && past.length > 0) lastVisit.textContent = `Last visit: ${past[past.length-1].appointment_date}`;
                }
            } catch (err) { console.error("Stats load error:", err); }
        };
        fetchDashboardStats();
    }

    // --- Profile Logic ---
    if (page === 'profile.html' || path.includes('profile.html')) {
        const profileForm = document.getElementById('profileForm');
        const fetchProfile = async () => {
            try {
                const res = await authFetch(`${API_BASE_URL}/user/profile`);
                if (!res.ok) return;
                const data = await res.json();
                
                if (document.getElementById('fullName')) document.getElementById('fullName').value = data.fullName || '';
                if (document.getElementById('email')) document.getElementById('email').value = data.email || '';
                if (document.getElementById('phone')) document.getElementById('phone').value = data.phone || '';
                if (document.getElementById('dob')) document.getElementById('dob').value = data.dob || '';
                if (document.getElementById('gender')) document.getElementById('gender').value = data.gender || '';
                if (document.getElementById('bloodGroup')) document.getElementById('bloodGroup').value = data.bloodGroup || '';
                if (document.getElementById('emergencyContact')) document.getElementById('emergencyContact').value = data.emergencyContact || '';
                if (document.getElementById('address')) document.getElementById('address').value = data.address || '';
                
                if (data.profilePic && document.getElementById('avatarImg')) {
                    document.getElementById('avatarImg').src = data.profilePic;
                }
                if (data.id && document.getElementById('sidebarId')) {
                    document.getElementById('sidebarId').textContent = `ID: ${data.id.substring(0, 8).toUpperCase()}`;
                }
            } catch (err) { console.error("Profile load error:", err); }
        };
        fetchProfile();

        const editBtn = document.getElementById('editProfileBtn');
        const cancelBtn = document.getElementById('cancelEditBtn');
        const saveBtn = document.getElementById('saveProfileBtn');
        const editAvatarBtn = document.getElementById('editAvatarBtn');
        const avatarUpload = document.getElementById('avatarUpload');
        const avatarImg = document.getElementById('avatarImg');

        if (editBtn) {
            editBtn.addEventListener('click', () => {
                profileForm.querySelectorAll('input, select, textarea').forEach(i => i.disabled = false);
                editBtn.style.display = 'none';
                cancelBtn.style.display = 'inline-block';
                saveBtn.style.display = 'inline-block';
            });
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                fetchProfile();
                profileForm.querySelectorAll('input, select, textarea').forEach(i => i.disabled = true);
                editBtn.style.display = 'inline-block';
                cancelBtn.style.display = 'none';
                saveBtn.style.display = 'none';
            });
        }

        if (editAvatarBtn) {
            editAvatarBtn.addEventListener('click', () => avatarUpload.click());
        }

        if (avatarUpload) {
            avatarUpload.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = async (e) => {
                        const base64Image = e.target.result;
                        avatarImg.src = base64Image;
                        
                        // Auto-save avatar change
                        try {
                            await authFetch(`${API_BASE_URL}/user/profile`, {
                                method: 'PUT',
                                body: JSON.stringify({ profilePic: base64Image })
                            });
                        } catch (err) { console.error("Avatar upload failed:", err); }
                    };
                    reader.readAsDataURL(file);
                }
            });
        }

        if (profileForm) {
            profileForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const saveBtn = document.getElementById('saveProfileBtn');
                if (saveBtn) saveBtn.classList.add('btn-loading');

                const payload = Object.fromEntries(new FormData(profileForm).entries());
                try {
                    const res = await authFetch(`${API_BASE_URL}/user/profile`, {
                        method: 'PUT',
                        body: JSON.stringify(payload)
                    });
                    if (!res.ok) throw new Error("Update failed");
                    
                    const notification = document.getElementById('profileNotification');
                    if (notification) {
                        notification.className = 'notification success show';
                        notification.textContent = 'Profile successfully updated!';
                    }
                    
                    if (document.getElementById('navUserName')) document.getElementById('navUserName').textContent = payload.fullName;
                    if (document.getElementById('sidebarName')) document.getElementById('sidebarName').textContent = payload.fullName;

                    if (notification) setTimeout(() => notification.classList.remove('show'), 3000);
                } catch (err) {
                    alert("Failed to update profile.");
                } finally {
                    if (saveBtn) saveBtn.classList.remove('btn-loading');
                    profileForm.querySelectorAll('input, select, textarea').forEach(i => i.disabled = true);
                    if (document.getElementById('editProfileBtn')) document.getElementById('editProfileBtn').style.display = 'inline-block';
                    if (document.getElementById('cancelEditBtn')) document.getElementById('cancelEditBtn').style.display = 'none';
                    if (saveBtn) saveBtn.style.display = 'none';
                }
            });
        }
    }
});
