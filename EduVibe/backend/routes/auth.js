/**
 * Auth Routes – /api/auth
 * POST /register  – create account
 * POST /login     – get JWT
 * GET  /me        – get current user (protected)
 */

const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const { users } = require('../db');
const { validateAge, validateEmail, validatePassword } = require('../validation');
const { authenticate } = require('../middleware/auth');

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'eduvibe_dev_secret_2026';
const JWT_EXPIRES = '7d';

// ─── POST /api/auth/register ──────────────────────────────────────────────────
router.post('/register', async (req, res) => {
    try {
        const { fullName, email, age, password, phone, linkedin } = req.body;

        // ── Field presence ───────────────────────────────────────────────────
        if (!fullName || !email || !age || !password) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields: fullName, email, age, password.',
            });
        }

        // ── Business-rule validation (same as frontend validation.js) ────────
        if (!validateEmail(email)) {
            return res.status(400).json({
                success: false,
                error: 'Invalid email format.',
            });
        }

        if (!validateAge(Number(age))) {
            return res.status(400).json({
                success: false,
                error: 'EduVibe programs are for professionals aged 18–30.',
            });
        }

        if (!validatePassword(password)) {
            return res.status(400).json({
                success: false,
                error: 'Password must be at least 8 characters and include letters and numbers.',
            });
        }

        // ── Duplicate check ──────────────────────────────────────────────────
        const existing = users.find(u => u.email.toLowerCase() === email.toLowerCase());
        if (existing) {
            return res.status(409).json({
                success: false,
                error: 'An account with that email already exists.',
            });
        }

        // ── Hash password & persist ──────────────────────────────────────────
        const passwordHash = await bcrypt.hash(password, 12);
        const user = {
            id: uuidv4(),
            fullName: fullName.trim(),
            email: email.toLowerCase().trim(),
            age: Number(age),
            phone: phone || null,
            linkedin: linkedin || null,
            passwordHash,
            role: 'student',
            joinedAt: new Date().toISOString(),
            avatarInitials: fullName.trim().split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase(),
        };
        users.push(user);

        // ── Issue token ──────────────────────────────────────────────────────
        const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, { expiresIn: JWT_EXPIRES });

        return res.status(201).json({
            success: true,
            message: `Welcome to EduVibe, ${user.fullName}! Your account is ready.`,
            token,
            user: sanitizeUser(user),
        });
    } catch (err) {
        console.error('[/register]', err);
        return res.status(500).json({ success: false, error: 'Internal server error.' });
    }
});

// ─── POST /api/auth/login ────────────────────────────────────────────────────
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ success: false, error: 'Email and password are required.' });
        }

        const user = users.find(u => u.email === email.toLowerCase().trim());
        if (!user) {
            return res.status(401).json({ success: false, error: 'Invalid credentials.' });
        }

        const match = await bcrypt.compare(password, user.passwordHash);
        if (!match) {
            return res.status(401).json({ success: false, error: 'Invalid credentials.' });
        }

        const token = jwt.sign({ userId: user.id, role: user.role }, JWT_SECRET, { expiresIn: JWT_EXPIRES });

        return res.json({
            success: true,
            message: `Welcome back, ${user.fullName}!`,
            token,
            user: sanitizeUser(user),
        });
    } catch (err) {
        console.error('[/login]', err);
        return res.status(500).json({ success: false, error: 'Internal server error.' });
    }
});

// ─── GET /api/auth/me ─────────────────────────────────────────────────────────
router.get('/me', authenticate, (req, res) => {
    const user = users.find(u => u.id === req.user.userId);
    if (!user) return res.status(404).json({ success: false, error: 'User not found.' });
    return res.json({ success: true, user: sanitizeUser(user) });
});

// ─── Helper: strip password hash before sending ───────────────────────────────
function sanitizeUser(user) {
    const { passwordHash, ...safe } = user;
    return safe;
}

module.exports = router;
