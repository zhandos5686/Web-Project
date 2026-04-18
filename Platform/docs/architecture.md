# Architecture And Defense Notes

This document explains the V1 structure of the English Learning Platform in a way that is useful during project defense.

## Project Idea
The platform helps students learn English through structured courses. A student can register, enroll in a course, open lessons, watch YouTube lesson links, complete quizzes, submit written tasks, track progress, and book live lesson slots. A teacher can create educational content and create live lesson slots.

V1 is intentionally simple. It proves the main architecture and user flows without AI, payments, notifications, or production deployment complexity.

## Backend Architecture
The backend is a Django REST Framework API split into domain apps:

- `users`: authentication, user profiles, and student/teacher role ownership.
- `courses`: public catalog data: categories, courses, modules, and lessons.
- `learning`: enrollments, lesson completions, progress, quizzes, written tasks, and submissions.
- `booking`: teacher live lesson slots and student bookings.

Each Django app follows the same pattern:

- `models.py`: database tables and relationships.
- `serializers.py`: converts model objects to JSON and validates request data.
- `views.py`: API logic and permission checks.
- `urls.py`: endpoints for that app.
- `tests.py`: backend behavior checks.
- `admin.py`: Django admin registration.

The root `config/urls.py` mounts all APIs under `/api/`.

## Frontend Architecture
The frontend is an Angular standalone-component app.

- `core`: services, route guards, and the API interceptor.
- `shared`: reusable UI components, currently the navbar.
- `features`: real page-level areas such as auth, catalog, lesson, progress, teacher dashboard, and booking.

The route table lives in `frontend/src/app/app.routes.ts`. Each route points to a feature component. Protected pages use route guards.

## Frontend And Backend Connection
Angular components do not call `HttpClient` directly. They use service classes:

- `AuthService`
- `CourseService`
- `EnrollmentService`
- `ProgressService`
- `LessonActivityService`
- `TeacherContentService`
- `BookingService`

Those services call relative API paths such as:

```ts
this.api.get('/courses/courses/')
```

The interceptor in `core/interceptors/api-prefix.interceptor.ts` changes that into:

```text
http://127.0.0.1:8000/api/courses/courses/
```

If the user is logged in, the same interceptor adds:

```text
Authorization: Token <token>
```

This keeps API connection logic in one place.

## Authentication And Roles
Authentication uses DRF token authentication.

Main endpoints:

- `POST /api/users/auth/register/`
- `POST /api/users/auth/login/`
- `GET /api/users/auth/me/`
- `POST /api/users/auth/logout/`

Every registered Django `User` has a `UserProfile`. The profile stores:

- `role`: `student` or `teacher`
- `bio`: short profile text

Role checks are explicit:

- Student-only actions check `UserProfile.role == student`.
- Teacher-only actions use `IsTeacher`.
- Route guards protect Angular pages before the user reaches them.

## Main User Flows
Student flow:

1. Student logs in or registers.
2. Student opens the catalog.
3. Student opens a course detail page.
4. Student sends an enrollment request.
5. Student waits until the teacher approves the request.
6. After approval, student sees the course in My Courses.
7. Student opens a lesson.
8. Student marks the lesson as completed.
9. Student submits quiz answers and receives a score.
10. Student submits a written task answer.
11. Student checks Progress and My Tasks.
12. Student opens Booking and books an available slot.

Teacher flow:

1. Teacher logs in.
2. Teacher opens Teacher Dashboard.
3. Teacher approves or rejects enrollment requests.
4. Teacher views student progress for approved enrollments.
5. Teacher creates a course.
6. Teacher creates a module.
7. Teacher creates a lesson.
8. Teacher creates a quiz, questions, choices, and a written task.
9. Teacher views quiz and written task submissions from their own courses.
10. Teacher opens Booking.
11. Teacher creates a live lesson slot with a meeting link.
12. Teacher deletes an unbooked slot if the time was created by mistake.
13. Teacher views bookings on their own slots.

## API Areas
Auth:

- `/api/users/auth/register/`
- `/api/users/auth/login/`
- `/api/users/auth/me/`
- `/api/users/auth/logout/`

Courses:

- `/api/courses/categories/`
- `/api/courses/courses/`
- `/api/courses/courses/<id>/`
- `/api/courses/lessons/<id>/`
- `/api/courses/teacher/courses/`
- `/api/courses/teacher/modules/`
- `/api/courses/teacher/lessons/`

Learning:

- `/api/learning/enroll/<course_id>/`
- `/api/learning/my-courses/`
- `/api/learning/my-enrollment-requests/`
- `/api/learning/my-task-submissions/`
- `/api/learning/lessons/<lesson_id>/complete/`
- `/api/learning/progress-summary/`
- `/api/learning/lessons/<lesson_id>/quiz/`
- `/api/learning/lessons/<lesson_id>/quiz/submit/`
- `/api/learning/lessons/<lesson_id>/task/`
- `/api/learning/lessons/<lesson_id>/task/submit/`
- `/api/learning/teacher/quizzes/`
- `/api/learning/teacher/questions/`
- `/api/learning/teacher/choices/`
- `/api/learning/teacher/tasks/`
- `/api/learning/teacher/enrollment-requests/`
- `/api/learning/teacher/enrollment-requests/<request_id>/<approve|reject>/`
- `/api/learning/teacher/student-progress/`
- `/api/learning/teacher/quiz-submissions/`
- `/api/learning/teacher/task-submissions/`

Booking:

- `/api/booking/teacher/slots/`
- `/api/booking/teacher/slots/<slot_id>/`
- `/api/booking/teacher/my-slots/`
- `/api/booking/teacher/bookings/`
- `/api/booking/available-slots/`
- `/api/booking/book/<slot_id>/`
- `/api/booking/my-bookings/`

## Data Protection Rules
The backend does not trust the frontend. Important checks happen on the backend:

- Anonymous users cannot enroll, complete lessons, submit quizzes/tasks, or use booking.
- Teachers cannot submit student activities.
- Students cannot use teacher content-management endpoints.
- Students can submit lesson activities only for courses where they are enrolled.
- Student enrollment requests do not create access until a teacher approves them.
- Teachers can approve/reject enrollment requests only for their own courses.
- Teachers can view progress only for students enrolled in their own courses.
- Teachers can add content only to courses/modules/lessons they own.
- A slot can be booked only once because `Booking.slot` is a one-to-one relationship.
- A teacher can delete only their own unbooked slots. Booked slots are kept as booking history in V1.

## Demo Data
The seed command creates:

- `demo_teacher` with password `TeacherPass123`
- `demo_student` with password `StudentPass123`
- realistic English categories
- published courses
- modules and lessons
- YouTube lesson URLs
- quiz and written task examples
- one approved demo student enrollment request
- one demo student enrollment
- one completed lesson
- one submitted written task
- available live lesson slots with meeting links

Run:

```bash
cd Platform/backend
source .venv/bin/activate
python manage.py seed_demo_data
```

## Defense Demo Scenario
1. Start backend and frontend.
2. Open the home page and describe the goal of V1.
3. Show the catalog and course detail page.
4. Log in as `demo_student`.
5. Show My Courses, Lesson, Quiz, Task, Progress, My Tasks, and Booking.
6. Log out.
7. Log in as `demo_teacher`.
8. Show Teacher Dashboard enrollment approval, student progress, content creation, and student submissions.
9. Show teacher booking slot creation, meeting link, delete for unbooked slots, and bookings.
10. Explain that AI, payments, notifications, grading UI, and deployment are future versions.

## Future Versions
Good next steps after V1:

1. Add teacher update/delete screens.
2. Add written task review and scoring.
3. Add booking cancellation/rescheduling.
4. Add richer lesson video embedding.
5. Add production settings and deployment.
6. Add AI only after the base learning platform is stable.
