/**
 * EduVibe Backend Validation Helpers
 * Mirrors the rules from the frontend validation.js so that
 * the API enforces the exact same constraints.
 */

/**
 * Validates the age of a student for registration.
 * @param {number} age - The age of the student.
 * @returns {boolean} - true if valid, false otherwise.
 */
const validateAge = (age) => {
    return age >= 18 && age <= 30;
};

/**
 * Validates the email format.
 * @param {string} email
 * @returns {boolean}
 */
const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
};

/**
 * Validates password strength (min 8 characters, at least one letter and one number).
 * @param {string} password
 * @returns {boolean}
 */
const validatePassword = (password) => {
    return password.length >= 8 && /[a-zA-Z]/.test(password) && /[0-9]/.test(password);
};

module.exports = { validateAge, validateEmail, validatePassword };
