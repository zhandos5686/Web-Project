from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Category, Course, Lesson, Module
from users.models import UserProfile

class CoursesAppSmokeTest(TestCase):
    def test_app_placeholder(self):
        self.assertTrue(True)


class CourseCatalogApiTest(TestCase):
    def test_course_catalog_returns_nested_course_data(self):
        category = Category.objects.create(name="Speaking", description="Speaking practice")
        course = Course.objects.create(
            category=category,
            title="English Speaking A1",
            description="Build simple speaking confidence.",
            level="A1",
            image_url="https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
            is_published=True,
        )
        module = Module.objects.create(course=course, title="Introductions", order=1)
        Lesson.objects.create(
            module=module,
            title="Saying hello",
            youtube_url="https://www.youtube.com/watch?v=HAnw168huqA",
            order=1,
        )

        response = self.client.get(reverse("course-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["category"]["name"], "Speaking")
        self.assertEqual(response.data[0]["modules"][0]["lessons"][0]["title"], "Saying hello")


class TeacherCourseManagementApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(username="teacher_content", password="StrongPass123")
        self.student = User.objects.create_user(username="student_content", password="StrongPass123")
        UserProfile.objects.update_or_create(
            user=self.teacher,
            defaults={"role": UserProfile.Role.TEACHER},
        )
        UserProfile.objects.update_or_create(
            user=self.student,
            defaults={"role": UserProfile.Role.STUDENT},
        )

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_teacher_can_create_course_module_and_lesson(self):
        self.authenticate(self.teacher)

        course_response = self.client.post(
            reverse("teacher-create-course"),
            {
                "title": "Teacher Course",
                "description": "Created by teacher.",
                "level": "B1",
                "category_name": "Teacher Demo",
                "is_published": True,
            },
            format="json",
        )
        self.assertEqual(course_response.status_code, 201)
        course = Course.objects.get(id=course_response.data["id"])
        self.assertEqual(course.teacher, self.teacher)
        self.assertEqual(course.category.name, "Teacher Demo")

        module_response = self.client.post(
            reverse("teacher-create-module"),
            {
                "course": course.id,
                "title": "Teacher Module",
                "order": 1,
            },
            format="json",
        )
        self.assertEqual(module_response.status_code, 201)

        lesson_response = self.client.post(
            reverse("teacher-create-lesson"),
            {
                "module": module_response.data["id"],
                "title": "Teacher Lesson",
                "youtube_url": "https://www.youtube.com/watch?v=HAnw168huqA",
                "content": "Lesson content.",
                "order": 1,
            },
            format="json",
        )
        self.assertEqual(lesson_response.status_code, 201)
        self.assertEqual(Lesson.objects.get(id=lesson_response.data["id"]).module.course, course)

    def test_student_cannot_use_teacher_course_endpoints(self):
        self.authenticate(self.student)
        response = self.client.post(
            reverse("teacher-create-course"),
            {"title": "Blocked", "is_published": True},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_add_module_to_another_teachers_course(self):
        other_teacher = User.objects.create_user(username="other_teacher", password="StrongPass123")
        UserProfile.objects.update_or_create(
            user=other_teacher,
            defaults={"role": UserProfile.Role.TEACHER},
        )
        other_course = Course.objects.create(title="Other Course", teacher=other_teacher, is_published=True)

        self.authenticate(self.teacher)
        response = self.client.post(
            reverse("teacher-create-module"),
            {"course": other_course.id, "title": "Blocked Module", "order": 1},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
