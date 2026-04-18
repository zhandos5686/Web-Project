from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import UserProfile


class UsersAppSmokeTest(TestCase):
    def test_app_placeholder(self):
        self.assertTrue(True)


class AuthApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_login_current_user_and_logout(self):
        register_response = self.client.post(
            reverse("auth-register"),
            {
                "username": "student1",
                "email": "student1@example.com",
                "password": "StrongPass123",
                "role": UserProfile.Role.STUDENT,
                "bio": "English learner",
            },
            format="json",
        )

        self.assertEqual(register_response.status_code, 201)
        self.assertIn("token", register_response.data)
        self.assertEqual(register_response.data["user"]["role"], UserProfile.Role.STUDENT)

        login_response = self.client.post(
            reverse("auth-login"),
            {"username": "student1", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        token = login_response.data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        current_user_response = self.client.get(reverse("auth-current-user"))

        self.assertEqual(current_user_response.status_code, 200)
        self.assertEqual(current_user_response.data["username"], "student1")
        self.assertEqual(current_user_response.data["email"], "student1@example.com")

        logout_response = self.client.post(reverse("auth-logout"))
        self.assertEqual(logout_response.status_code, 200)

        current_user_after_logout_response = self.client.get(reverse("auth-current-user"))
        self.assertEqual(current_user_after_logout_response.status_code, 401)
