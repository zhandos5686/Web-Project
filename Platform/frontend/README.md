# Frontend

Angular application for the English Learning Platform.

## Structure
- `core`: app-level services, interceptors, and single-instance logic.
- `shared`: reusable UI components.
- `features`: route-level feature areas such as home, auth, catalog, lesson, progress, teacher, and booking.

## Authentication
`AuthService` stores JWT `access_token` and `refresh_token` values in local storage, loads the current user from the backend, and exposes auth state to components and route guards.

The HTTP interceptor sends authenticated API requests with `Authorization: Bearer <access_token>`. When an API request returns `401`, it uses the refresh token to request a new access token, retries the original request once, and clears auth state if refresh fails.

Protected student pages use `authGuard`. The teacher dashboard uses `teacherGuard`.

The navbar is role-aware: students see learning pages, teachers see the teacher dashboard, and guests see only public entry points.

## Run
```bash
npm install
npm start
```

The app runs on `http://localhost:4200/` and reads the API base URL from `src/environments/environment.ts`.
