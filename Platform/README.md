# English Learning Platform

Defense-ready V1 of a full-stack English learning platform.

The project uses Django REST Framework for the backend API and Angular for the frontend SPA. V1 focuses on a clear, explainable learning flow instead of advanced features.

## Stack
- Backend: Django 6, Django REST Framework, DRF token authentication
- Frontend: Angular 21 standalone components
- Database: SQLite for local development and defense demo

## Implemented V1 Scope
- Authentication with register, login, current user, logout, and password reset.
- Student and teacher roles through `UserProfile`.
- Course catalog with demo categories, courses, modules, lessons, and YouTube URLs.
- Course detail page with nested modules and lesson links.
- Student enrollment request flow with teacher approval/rejection and My Courses page for approved courses.
- Lesson page with completion tracking.
- Progress page with per-course percentage.
- Lesson quiz submission with score calculation.
- Written task submission, My Tasks history, and teacher review with score/feedback.
- Teacher dashboard for creating courses, modules, lessons, quizzes, questions, choices, and written tasks.
- Teacher view of enrollment requests, student progress, quiz submissions, and written task submissions for their own courses.
- Booking page where teachers create/delete available live lesson slots with meeting links and students book them.
- In-app notifications for booking, written task submission, and task review events.
- Demo seed command with realistic content and demo accounts.

## Intentionally Not Included In V1
- AI features.
- Payments.
- Calendar integrations.
- Course update/delete UI.
- Booking cancellation/rescheduling for already booked slots.
- Production deployment settings.

## Project Layout
- `backend/`: Django REST API.
- `backend/users/`: authentication, profile, and role logic.
- `backend/courses/`: catalog, categories, courses, modules, lessons, and demo seed data.
- `backend/learning/`: enrollments, progress, quizzes, written tasks, and submissions.
- `backend/booking/`: live lesson slots and bookings.
- `frontend/`: Angular single-page application.
- `frontend/src/app/core/`: API, auth, feature services, guards, and interceptors.
- `frontend/src/app/shared/`: reusable UI, currently the navbar.
- `frontend/src/app/features/`: route-level pages.
- `docs/`: architecture and defense notes.

## Run Backend
```bash
cd Platform/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

Backend API starts at `http://127.0.0.1:8000/api/`.

## Run Frontend
```bash
cd Platform/frontend
npm install
npm start
```

Frontend starts at `http://localhost:4200/`.

## Demo Accounts
Created by:

```bash
python manage.py seed_demo_data
```

- Student: `demo_student` / `StudentPass123`
- Teacher: `demo_teacher` / `TeacherPass123`

## Main API Areas
- Auth: `/api/users/auth/...`
- Password reset request: `/api/users/auth/forgot-password/`
- Password reset confirm: `/api/users/auth/reset-password/`
- Catalog and lessons: `/api/courses/...`
- Learning: `/api/learning/...`
- Booking: `/api/booking/...`

## Password Reset Demo Flow
The backend uses Django's built-in password reset token generator with a base64 encoded user id.
In local development, email uses Django's console email backend by default, so the reset link is printed in the backend terminal.
When `DEBUG=True`, the forgot-password API response also includes `reset_url` to make defense/demo testing easier.

Frontend routes:
- `/forgot-password`: request a reset link by email.
- `/reset-password?uid=...&token=...`: set a new password from the generated link.

Angular sends API requests through service classes. The API prefix interceptor adds the backend base URL and the auth interceptor behavior is handled by the existing API prefix/token setup.

## Recommended Defense Demo
1. Open the home page and explain the V1 goal.
2. Open Catalog and show real seeded courses.
3. Open a course detail page and show modules, lessons, and YouTube URLs.
4. Log in as `demo_student`.
5. Open My Courses and show the seeded enrollment.
6. Send an enrollment request for another course and explain that it stays pending until teacher approval.
7. Open a lesson, submit/inspect quiz and written task, and mark the lesson complete.
8. Open Progress and show calculated completion percentage.
9. Open My Tasks and show submitted written answers.
10. Open Booking and book an available teacher slot.
11. Log out and log in as `demo_teacher`.
12. Open Teacher Dashboard and approve/reject enrollment requests.
13. Show student progress and quiz/task submissions in Teacher Dashboard.
14. Open Booking and show teacher slot creation, meeting links, deletion of unbooked slots, and bookings on teacher slots.

## Development Strategy
1. Keep backend business areas separated by Django app.
2. Keep Angular UI separated by feature page.
3. Keep role checks explicit and easy to explain.
4. Add advanced features only after V1 behavior is stable.
