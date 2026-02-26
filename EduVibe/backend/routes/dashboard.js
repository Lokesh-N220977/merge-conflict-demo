/**
 * Dashboard Routes – /api/dashboard
 * GET  /           – full dashboard data for the authenticated user
 * GET  /stats      – quick stats (enrollments, progress, streak)
 */

const express = require('express');
const { users, courses, enrollments, quizSubmissions } = require('../db');
const { authenticate } = require('../middleware/auth');

const router = express.Router();

// ─── GET /api/dashboard ───────────────────────────────────────────────────────
router.get('/', authenticate, (req, res) => {
    const userId = req.user.userId;

    // User record
    const user = users.find(u => u.id === userId);
    if (!user) return res.status(404).json({ success: false, error: 'User not found.' });

    // Enrolled courses with their details
    const userEnrollments = enrollments.filter(e => e.userId === userId);
    const enrolledCourses = userEnrollments.map(enr => {
        const course = courses.find(c => c.id === enr.courseId);
        return {
            enrollment: enr,
            course: course || null,
        };
    });

    // Quiz history
    const quizHistory = quizSubmissions.filter(q => q.userId === userId);

    // Compute aggregate stats
    const totalEnrolled = userEnrollments.length;
    const avgProgress =
        totalEnrolled === 0
            ? 0
            : Math.round(
                userEnrollments.reduce((sum, e) => sum + e.progress, 0) / totalEnrolled
            );
    const completed = userEnrollments.filter(e => e.progress === 100).length;

    // Streak calculation (days since first enrollment)
    const streak = totalEnrolled > 0 ? Math.floor(Math.random() * 14) + 1 : 0; // demo streak

    return res.json({
        success: true,
        user: sanitizeUser(user),
        stats: {
            totalEnrolled,
            avgProgress,
            completed,
            streak,
            quizzesTaken: quizHistory.length,
        },
        enrolledCourses,
        quizHistory,
    });
});

// ─── GET /api/dashboard/stats ─────────────────────────────────────────────────
router.get('/stats', authenticate, (req, res) => {
    const userId = req.user.userId;
    const userEnrollments = enrollments.filter(e => e.userId === userId);
    const totalEnrolled = userEnrollments.length;
    const avgProgress =
        totalEnrolled === 0
            ? 0
            : Math.round(
                userEnrollments.reduce((sum, e) => sum + e.progress, 0) / totalEnrolled
            );
    const completed = userEnrollments.filter(e => e.progress === 100).length;

    return res.json({
        success: true,
        stats: { totalEnrolled, avgProgress, completed },
    });
});

function sanitizeUser(user) {
    const { passwordHash, ...safe } = user;
    return safe;
}

module.exports = router;
