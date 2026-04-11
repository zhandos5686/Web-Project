# Learning Platform

Learning Platform is a full-stack educational web application built with Angular and Django REST Framework.

## Team Members
- Amanzhol Akezhan
- Shirinbek Shugyla
- Makhanbetzhan Zhandos

## Project Description
The platform allows users to log in, browse courses, enroll in courses, view their own courses, check tasks, mark tasks as completed, and edit their profile.

## Tech Stack

### Frontend
- Angular
- TypeScript
- HttpClient
- Routing
- FormsModule

### Backend
- Django
- Django REST Framework
- JWT Authentication
- django-cors-headers
- SQLite

## Main Features
- JWT login and logout
- Course catalog
- My courses page
- Tasks page
- Profile page
- Full CRUD for courses
- Enroll in courses
- Mark tasks as completed

## Backend Models
- Profile
- Category
- Course
- Enrollment
- Task
- Submission

## API Requirements Covered
- At least 4 models
- At least 2 ForeignKey relationships
- At least 2 Serializer classes
- At least 2 ModelSerializer classes
- At least 2 FBV endpoints
- At least 2 CBV endpoints
- Full CRUD for one model
- JWT authentication
- CORS configuration

## Frontend Requirements Covered
- Interfaces and services
- API requests from click events
- ngModel forms
- Routing with multiple pages
- @for / @if rendering
- HttpClient service
- Error handling

## Repository Structure
- `frontend/` — Angular application
- `backend/` — Django REST Framework application
- `postman/` — Postman collection
- `README.md` — project overview and setup instructions

## How to Run Backend
1. Open the `backend/` folder
2. Create a virtual environment
3. Install dependencies from `requirements.txt`
4. Run migrations
5. Start Django development server

Example:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
