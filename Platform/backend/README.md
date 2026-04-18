# Backend

Django REST Framework API for the English Learning Platform.

## Apps
- `users`: authentication, profile, and role ownership.
- `courses`: course catalog, modules, and lessons.
- `learning`: quizzes, tasks, enrollments, and progress.
- `booking`: teacher live lesson slots and bookings.

## Authentication
The V1 API uses DRF token authentication.

- Register: `POST /api/users/auth/register/`
- Login: `POST /api/users/auth/login/`
- Current user: `GET /api/users/auth/me/`
- Logout: `POST /api/users/auth/logout/`

Registration creates a Django user and a matching `UserProfile` with the selected role.

## Run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

## API Root
`http://127.0.0.1:8000/api/`

## Demo Accounts
- Teacher: `demo_teacher` / `TeacherPass123`
- Student: `demo_student` / `StudentPass123`
