/**
 * JWT Authentication Middleware
 * Attaches req.user = { userId, role } for protected routes.
 */

const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'eduvibe_dev_secret_2026';

const authenticate = (req, res, next) => {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.status(401).json({
            success: false,
            error: 'Access denied. No token provided. Attach: Authorization: Bearer <token>',
        });
    }

    const token = authHeader.split(' ')[1];

    try {
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = decoded; // { userId, role, iat, exp }
        return next();
    } catch (err) {
        return res.status(401).json({
            success: false,
            error: 'Invalid or expired token. Please log in again.',
        });
    }
};

module.exports = { authenticate };
