/**
 * EduVibe Backend – Express Server Entry Point
 * 
 * Run:   node server.js
 * Dev:   npx nodemon server.js
 * 
 * Base URL: http://localhost:5000/api
 */

const express = require('express');
const cors = require('cors');

// ── Route modules ─────────────────────────────────────────────────────────────
const authRoutes = require('./routes/auth');
const coursesRoutes = require('./routes/courses');
const dashboardRoutes = require('./routes/dashboard');
const quizRoutes = require('./routes/quiz');
const contactRoutes = require('./routes/contact');

const PORT = process.env.PORT || 5000;
const app = express();

// ── Global Middleware ──────────────────────────────────────────────────────────
app.use(cors({
    origin: '*',      // In production, restrict to your frontend domain
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ── Request logger (dev) ──────────────────────────────────────────────────────
app.use((req, _res, next) => {
    const ts = new Date().toLocaleTimeString();
    console.log(`[${ts}] ${req.method} ${req.path}`);
    next();
});

// ── Health Check ──────────────────────────────────────────────────────────────
app.get('/api/health', (_req, res) => {
    res.json({
        status: 'ok',
        service: 'EduVibe API',
        version: '1.0.0',
        timestamp: new Date().toISOString(),
    });
});

// ── API Routes ────────────────────────────────────────────────────────────────
app.use('/api/auth', authRoutes);
app.use('/api/courses', coursesRoutes);
app.use('/api/dashboard', dashboardRoutes);
app.use('/api/quiz', quizRoutes);
app.use('/api/contact', contactRoutes);

// ── Root ──────────────────────────────────────────────────────────────────────
app.get('/', (_req, res) => {
    res.json({
        name: 'EduVibe Backend API',
        version: '1.0.0',
        endpoints: {
            health: 'GET  /api/health',
            register: 'POST /api/auth/register',
            login: 'POST /api/auth/login',
            me: 'GET  /api/auth/me            [Bearer]',
            courses: 'GET  /api/courses            [?category=]',
            course: 'GET  /api/courses/:id',
            enroll: 'POST /api/courses/:id/enroll [Bearer]',
            progress: 'GET/PUT /api/courses/:id/progress [Bearer]',
            dashboard: 'GET  /api/dashboard          [Bearer]',
            stats: 'GET  /api/dashboard/stats    [Bearer]',
            quiz: 'POST /api/quiz/submit        [Bearer]',
            quizHist: 'GET  /api/quiz/history       [Bearer]',
            contact: 'POST /api/contact',
        },
    });
});

// ── 404 catch-all ─────────────────────────────────────────────────────────────
app.use((_req, res) => {
    res.status(404).json({ success: false, error: 'Route not found.' });
});

// ── Global error handler ──────────────────────────────────────────────────────
app.use((err, _req, res, _next) => {
    console.error('[Global Error]', err);
    res.status(500).json({ success: false, error: 'Something went wrong on the server.' });
});

// ── Start ─────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
    console.log('\n╔══════════════════════════════════════════╗');
    console.log('║        EduVibe Backend Running           ║');
    console.log(`║  http://localhost:${PORT}/api               ║`);
    console.log('╚══════════════════════════════════════════╝\n');
    console.log('  GET  /api/health       → Health check');
    console.log('  POST /api/auth/register');
    console.log('  POST /api/auth/login');
    console.log('  GET  /api/courses');
    console.log('  POST /api/quiz/submit');
    console.log('  POST /api/contact\n');
});

module.exports = app;
