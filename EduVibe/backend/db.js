/**
 * EduVibe Backend – In-Memory Data Store
 * 
 * Acts as a lightweight database for the demo.
 * Replace with a real DB (MongoDB/PostgreSQL) for production.
 */

const { v4: uuidv4 } = require('uuid');

// ─── Users ────────────────────────────────────────────────────────────────────
const users = [];

// ─── Courses ──────────────────────────────────────────────────────────────────
const courses = [
    {
        id: 'course-001',
        title: 'AI & Machine Learning Professional',
        category: 'Technology',
        duration: '12 weeks',
        price: 499,
        rating: 4.9,
        enrolled: 3847,
        badge: 'BESTSELLER',
        description:
            'Master neural networks, model deployment, and MLOps practices used at top engineering companies.',
        instructor: { name: 'Dr. Priya Sharma', title: 'Lead AI Research Scientist', avatar: 'PS' },
        modules: [
            { title: 'Foundations of Machine Learning', lessons: 8 },
            { title: 'Deep Neural Networks', lessons: 10 },
            { title: 'Model Training & Evaluation', lessons: 7 },
            { title: 'MLOps & Deployment', lessons: 9 },
        ],
        videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
    },
    {
        id: 'course-002',
        title: 'Strategic Project Management (PMP Prep)',
        category: 'Business',
        duration: '8 weeks',
        price: 349,
        rating: 4.8,
        enrolled: 5120,
        badge: 'TOP RATED',
        description:
            'An industry-aligned PMP prep track designed to help you pass the exam and apply skills on the job.',
        instructor: { name: 'James O\'Brien', title: 'PMP, Senior Program Manager', avatar: 'JO' },
        modules: [
            { title: 'Project Initiation & Scope', lessons: 6 },
            { title: 'Planning & Scheduling', lessons: 8 },
            { title: 'Risk Management', lessons: 5 },
            { title: 'Exam Preparation & Mock Tests', lessons: 10 },
        ],
        videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
    },
    {
        id: 'course-003',
        title: 'Data Science & Business Intelligence',
        category: 'Data',
        duration: '10 weeks',
        price: 429,
        rating: 4.7,
        enrolled: 4290,
        badge: null,
        description:
            'Python, SQL, Power BI, and statistical modeling — everything to become a data-driven decision maker.',
        instructor: { name: 'Ananya Krishnan', title: 'Data Scientist, ex-Google', avatar: 'AK' },
        modules: [
            { title: 'Python for Data Science', lessons: 9 },
            { title: 'SQL & Database Fundamentals', lessons: 7 },
            { title: 'Statistical Analysis', lessons: 6 },
            { title: 'Power BI & Dashboards', lessons: 8 },
        ],
        videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
    },
    {
        id: 'course-004',
        title: 'Cloud Architecture (AWS & Azure)',
        category: 'Technology',
        duration: '6 weeks',
        price: 379,
        rating: 4.8,
        enrolled: 2980,
        badge: null,
        description:
            'Design and deploy scalable cloud infrastructure aligned with AWS Solutions Architect and Azure certs.',
        instructor: { name: 'Carlos Martinez', title: 'AWS Certified Solutions Architect', avatar: 'CM' },
        modules: [
            { title: 'Cloud Fundamentals', lessons: 5 },
            { title: 'AWS Core Services', lessons: 8 },
            { title: 'Azure & Hybrid Cloud', lessons: 7 },
            { title: 'Security & Cost Optimization', lessons: 6 },
        ],
        videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
    },
    {
        id: 'course-005',
        title: 'Executive Communication & Influence',
        category: 'Leadership',
        duration: '5 weeks',
        price: 299,
        rating: 4.9,
        enrolled: 6120,
        badge: 'POPULAR',
        description:
            'Master the soft skills that separate individual contributors from leaders — negotiation, presence, and persuasion.',
        instructor: { name: 'Sarah Mitchell', title: 'Executive Coach, ex-McKinsey', avatar: 'SM' },
        modules: [
            { title: 'Executive Presence', lessons: 4 },
            { title: 'Storytelling & Narrative', lessons: 5 },
            { title: 'Negotiation Tactics', lessons: 6 },
            { title: 'Leading in the C-Suite', lessons: 4 },
        ],
        videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4',
    },
    {
        id: 'course-006',
        title: 'Cybersecurity Risk & Compliance',
        category: 'Data',
        duration: '7 weeks',
        price: 449,
        rating: 4.7,
        enrolled: 2210,
        badge: null,
        description:
            'Understand threat modeling, regulatory frameworks (GDPR, ISO 27001), and building organizational resilience.',
        instructor: { name: 'Lena Fischer', title: 'CISO & Cybersecurity Consultant', avatar: 'LF' },
        modules: [
            { title: 'Threat Modeling & Attack Surfaces', lessons: 7 },
            { title: 'GDPR & ISO 27001 Frameworks', lessons: 6 },
            { title: 'Incident Response', lessons: 5 },
            { title: 'Security Architecture', lessons: 8 },
        ],
        videoUrl: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4',
    },
];

// ─── Enrollments ──────────────────────────────────────────────────────────────
// { id, userId, courseId, enrolledAt, progress (0-100) }
const enrollments = [];

// ─── Quiz Submissions ─────────────────────────────────────────────────────────
// { id, userId, courseId, score, total, submittedAt }
const quizSubmissions = [];

// ─── Contact Messages ─────────────────────────────────────────────────────────
const contactMessages = [];

// ─── Helper: create new enrollment ───────────────────────────────────────────
const createEnrollment = (userId, courseId) => {
    const existing = enrollments.find(e => e.userId === userId && e.courseId === courseId);
    if (existing) return existing;
    const enrollment = {
        id: uuidv4(),
        userId,
        courseId,
        enrolledAt: new Date().toISOString(),
        progress: 0,
        currentLesson: 1,
    };
    enrollments.push(enrollment);
    return enrollment;
};

module.exports = {
    users,
    courses,
    enrollments,
    quizSubmissions,
    contactMessages,
    createEnrollment,
};
