/**
 * Contact Routes – /api/contact
 * POST /   – submit a contact / support message
 * GET  /   – list all messages (admin view, no auth guard for demo)
 */

const express = require('express');
const { v4: uuidv4 } = require('uuid');
const { contactMessages } = require('../db');

const router = express.Router();

// ─── POST /api/contact ────────────────────────────────────────────────────────
router.post('/', (req, res) => {
    const { name, email, subject, message } = req.body;

    if (!name || !email || !message) {
        return res.status(400).json({
            success: false,
            error: 'name, email, and message are required.',
        });
    }

    const entry = {
        id: uuidv4(),
        name: name.trim(),
        email: email.toLowerCase().trim(),
        subject: subject ? subject.trim() : 'General Inquiry',
        message: message.trim(),
        receivedAt: new Date().toISOString(),
        status: 'new',
    };
    contactMessages.push(entry);

    return res.status(201).json({
        success: true,
        message: 'Thank you for reaching out! Our team will respond within 1 business day.',
        ticketId: entry.id,
    });
});

// ─── GET /api/contact ─────────────────────────────────────────────────────────
router.get('/', (req, res) => {
    return res.json({ success: true, total: contactMessages.length, messages: contactMessages });
});

module.exports = router;
