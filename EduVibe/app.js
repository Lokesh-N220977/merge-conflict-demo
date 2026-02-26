import { validateAge, validateEmail, validatePassword } from './validation.js';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.padding = '1rem 4rem';
            navbar.style.background = 'rgba(255, 255, 255, 1)';
            navbar.style.boxShadow = '0 4px 6px rgba(0,0,0,0.05)';
        } else {
            navbar.style.padding = '1.5rem 4rem';
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // 2. Personalization
    const welcomeMessage = document.getElementById('welcomeMessage');
    if (welcomeMessage) {
        const userName = localStorage.getItem('registeredName');
        if (userName) {
            welcomeMessage.innerText = `Welcome back, ${userName}!`;
        }
    }

    // 3. Realistic Registration Flow
    const form = document.getElementById('registrationForm');
    const resultDiv = document.getElementById('result');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const name = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const age = parseInt(document.getElementById('age').value);
            const password = document.getElementById('password').value;

            // Clear previous results
            if (resultDiv) {
                resultDiv.style.opacity = '0';
                resultDiv.innerHTML = '';
            }

            // Client-side validation sequence
            if (!validateEmail(email)) {
                return showError("Please enter a valid institutional email.");
            }

            if (!validateAge(age)) {
                return showError("EduVibe programs are designed for professionals aged 18–25. Check our enterprise plans for other learners.");
            }

            if (!validatePassword(password)) {
                return showError("Password too weak. Use at least 8 characters with letters and numbers.");
            }

            // Visual feedback - Realistic loading
            setLoading(true);

            setTimeout(() => {
                // Success path
                localStorage.setItem('registeredName', name);
                showSuccess(`Welcome, ${name}! Your EduVibe account is ready. Redirecting to your dashboard...`);

                // Realistic redirect
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1800);
            }, 1200); // Fake API latency
        });
    }

    function setLoading(isLoading) {
        if (!submitBtn) return;
        if (isLoading) {
            submitBtn.disabled = true;
            btnText.innerHTML = '<span class="spinner"></span> Securing Connection...';
            submitBtn.style.opacity = '0.7';
        } else {
            submitBtn.disabled = false;
            btnText.innerText = 'Create Free Account';
            submitBtn.style.opacity = '1';
        }
    }

    function showError(message) {
        if (!resultDiv) return;
        resultDiv.style.display = 'block';
        resultDiv.style.opacity = '1';
        resultDiv.className = 'result-message result-denied';
        resultDiv.innerHTML = `<strong>Error:</strong> ${message}`;
    }

    function showSuccess(message) {
        if (!resultDiv) return;
        resultDiv.style.display = 'block';
        resultDiv.style.opacity = '1';
        resultDiv.className = 'result-message result-granted';
        resultDiv.innerHTML = `<strong>Success:</strong> ${message}`;
    }

    // 4. Logout Logic
    const logoutBtn = document.querySelector('nav .nav-cta');
    if (logoutBtn && logoutBtn.innerText.includes('Logout')) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('registeredName');
            window.location.href = 'index.html';
        });
    }
});

// Add spinner styles dynamically if not in CSS
const style = document.createElement('style');
style.innerHTML = `
    .spinner {
        display: inline-block;
        width: 1rem;
        height: 1rem;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
