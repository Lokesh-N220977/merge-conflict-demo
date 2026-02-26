# EduVibe Backend

A Node.js / Express REST API backend for the EduVibe professional certification platform.

---

## 🚀 Quick Start

```bash
cd backend
npm install
node server.js
# or for live-reload:
npx nodemon server.js
```

Server runs at **http://localhost:5000**

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET`  | `/api/health` | – | Health check |
| `POST` | `/api/auth/register` | – | Register new student |
| `POST` | `/api/auth/login` | – | Login, get JWT |
| `GET`  | `/api/auth/me` | Bearer | Current user info |
| `GET`  | `/api/courses` | – | List all courses (`?category=Technology`) |
| `GET`  | `/api/courses/:id` | – | Course detail |
| `POST` | `/api/courses/:id/enroll` | Bearer | Enroll in a course |
| `GET`  | `/api/courses/:id/progress` | Bearer | Get progress |
| `PUT`  | `/api/courses/:id/progress` | Bearer | Update progress |
| `GET`  | `/api/dashboard` | Bearer | Full dashboard |
| `GET`  | `/api/dashboard/stats` | Bearer | Quick stats |
| `POST` | `/api/quiz/submit` | Bearer | Submit quiz answers |
| `GET`  | `/api/quiz/history` | Bearer | Quiz history |
| `POST` | `/api/contact` | – | Contact/support form |

---

## 🔐 Authentication

Protected routes require an `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

Get a token by calling `POST /api/auth/register` or `POST /api/auth/login`.

---

## 📝 Example Requests

### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"fullName":"Arjun Kapoor","email":"arjun@company.com","age":24,"password":"Pass1234"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"arjun@company.com","password":"Pass1234"}'
```

### Get All Courses
```bash
curl http://localhost:5000/api/courses
```

### Enroll in a Course (with token)
```bash
curl -X POST http://localhost:5000/api/courses/course-001/enroll \
  -H "Authorization: Bearer <token>"
```

### Submit Quiz
```bash
curl -X POST http://localhost:5000/api/quiz/submit \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"courseId":"course-001","answers":{"q1":"b","q2":"c","q3":"a","q4":"b","q5":"d"}}'
```

---

## 📁 Folder Structure

```
backend/
├── server.js          ← Entry point
├── db.js              ← In-memory data store
├── validation.js      ← Server-side validation (mirrors frontend rules)
├── package.json
├── .env.example
├── middleware/
│   └── auth.js        ← JWT authentication middleware
└── routes/
    ├── auth.js        ← /api/auth
    ├── courses.js     ← /api/courses
    ├── dashboard.js   ← /api/dashboard
    ├── quiz.js        ← /api/quiz
    └── contact.js     ← /api/contact
```

---

## ✅ Validation Rules

The backend enforces the **same validation rules** as the frontend `validation.js`:

| Rule | Constraint |
|------|------------|
| **Age** | Must be between 18 and 30 |
| **Email** | Valid email format |
| **Password** | ≥ 8 chars, at least one letter + one number |

---

## ⚠️ Notes

- Data is stored **in-memory** — it resets on server restart.
- For production, swap `db.js` with MongoDB / PostgreSQL.
- Change `JWT_SECRET` to a strong random string in production.
