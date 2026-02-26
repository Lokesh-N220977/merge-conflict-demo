/**
 * Courses Routes – /api/courses
 * GET  /              – list all courses (optional ?category=)
 * GET  /:id           – course detail
 * POST /:id/enroll    – enroll authenticated user (protected)
 * GET  /:id/progress  – get progress for authenticated user (protected)
 * PUT  /:id/progress  – update lesson progress (protected)
 */

const express = require('express');
const { courses, enrollments, createEnrollment } = require('../db');
const { authenticate } = require('../middleware/auth');

const router = express.Router();

// ─── GET /api/courses ─────────────────────────────────────────────────────────
router.get('/', (req, res) => {
    const { category } = req.query;
    let result = courses;
    if (category && category !== 'All') {
        result = courses.filter(c => c.category.toLowerCase() === category.toLowerCase());
    }
    return res.json({ success: true, total: result.length, courses: result });
});

// ─── GET /api/courses/:id ─────────────────────────────────────────────────────
router.get('/:id', (req, res) => {
    const course = courses.find(c => c.id === req.params.id);
    if (!course) {
        return res.status(404).json({ success: false, error: 'Course not found.' });
    }
    return res.json({ success: true, course });
});

// ─── POST /api/courses/:id/enroll ─────────────────────────────────────────────
router.post('/:id/enroll', authenticate, (req, res) => {
    const course = courses.find(c => c.id === req.params.id);
    if (!course) {
        return res.status(404).json({ success: false, error: 'Course not found.' });
    }

    const enrollment = createEnrollment(req.user.userId, req.params.id);
    return res.status(201).json({
        success: true,
        message: `Successfully enrolled in "${course.title}"!`,
        enrollment,
    });
});

// ─── GET /api/courses/:id/progress ───────────────────────────────────────────
router.get('/:id/progress', authenticate, (req, res) => {
    const enrollment = enrollments.find(
        e => e.userId === req.user.userId && e.courseId === req.params.id
    );
    if (!enrollment) {
        return res.status(404).json({ success: false, error: 'Not enrolled in this course.' });
    }
    return res.json({ success: true, progress: enrollment });
});

// ─── PUT /api/courses/:id/progress ───────────────────────────────────────────
router.put('/:id/progress', authenticate, (req, res) => {
    const { progress, currentLesson } = req.body;

    const enrollment = enrollments.find(
        e => e.userId === req.user.userId && e.courseId === req.params.id
    );
    if (!enrollment) {
        return res.status(404).json({ success: false, error: 'Not enrolled in this course.' });
    }

    if (progress !== undefined) {
        enrollment.progress = Math.min(100, Math.max(0, Number(progress)));
    }
    if (currentLesson !== undefined) {
        enrollment.currentLesson = Number(currentLesson);
    }
    enrollment.updatedAt = new Date().toISOString();

    return res.json({ success: true, message: 'Progress updated.', progress: enrollment });
});

module.exports = router;
