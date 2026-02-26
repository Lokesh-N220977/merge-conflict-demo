/**
 * Quiz Routes – /api/quiz
 * POST /submit   – submit quiz answers and get score (protected)
 * GET  /history  – get all quiz submissions for the authenticated user (protected)
 */

const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { quizSubmissions, courses } = require('../db');
const { authenticate } = require('../middleware/auth');

const router = express.Router();

// ─── Answer key for demo quizzes (keyed by courseId) ─────────────────────────
const quizAnswerKeys = {
    'course-001': { q1: 'b', q2: 'c', q3: 'a', q4: 'b', q5: 'd' },
    'course-002': { q1: 'a', q2: 'a', q3: 'c', q4: 'b', q5: 'c' },
    'course-003': { q1: 'c', q2: 'b', q3: 'a', q4: 'd', q5: 'b' },
    'course-004': { q1: 'b', q2: 'c', q3: 'b', q4: 'a', q5: 'c' },
    'course-005': { q1: 'a', q2: 'd', q3: 'c', q4: 'b', q5: 'a' },
    'course-006': { q1: 'd', q2: 'b', q3: 'a', q4: 'c', q5: 'b' },
};

// ─── POST /api/quiz/submit ────────────────────────────────────────────────────
router.post('/submit', authenticate, (req, res) => {
    const { courseId, answers } = req.body;

    if (!courseId || !answers || typeof answers !== 'object') {
        return res.status(400).json({
            success: false,
            error: 'courseId and answers object are required.',
        });
    }

    const course = courses.find(c => c.id === courseId);
    if (!course) {
        return res.status(404).json({ success: false, error: 'Course not found.' });
    }

    const key = quizAnswerKeys[courseId] || {};
    const total = Object.keys(key).length || Object.keys(answers).length;
    let correct = 0;

    const breakdown = {};
    Object.entries(answers).forEach(([q, answer]) => {
        const isCorrect = key[q] === answer;
        if (isCorrect) correct++;
        breakdown[q] = { submitted: answer, correct: key[q] || null, isCorrect };
    });

    const score = total === 0 ? 0 : Math.round((correct / total) * 100);
    const passed = score >= 70;

    const submission = {
        id: uuidv4(),
        userId: req.user.userId,
        courseId,
        courseTitle: course.title,
        score,
        correct,
        total,
        passed,
        breakdown,
        submittedAt: new Date().toISOString(),
    };
    quizSubmissions.push(submission);

    return res.status(201).json({
        success: true,
        message: passed
            ? `Congratulations! You scored ${score}% and passed.`
            : `You scored ${score}%. A score of 70% or above is required to pass.`,
        result: submission,
    });
});

// ─── GET /api/quiz/history ────────────────────────────────────────────────────
router.get('/history', authenticate, (req, res) => {
    const userId = req.user.userId;
    const history = quizSubmissions
        .filter(q => q.userId === userId)
        .sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));

    return res.json({ success: true, total: history.length, history });
});

module.exports = router;
