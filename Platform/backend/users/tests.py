from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.test import TestCase, override_settings
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
        self.assertIn("access", register_response.data)
        self.assertIn("refresh", register_response.data)
        self.assertEqual(register_response.data["user"]["role"], UserProfile.Role.STUDENT)

        login_response = self.client.post(
            reverse("auth-login"),
            {"username": "student1", "password": "StrongPass123"},
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)
        access = login_response.data["access"]
        refresh = login_response.data["refresh"]

        refresh_response = self.client.post(
            reverse("auth-refresh"),
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        current_user_response = self.client.get(reverse("auth-current-user"))

        self.assertEqual(current_user_response.status_code, 200)
        self.assertEqual(current_user_response.data["username"], "student1")
        self.assertEqual(current_user_response.data["email"], "student1@example.com")

        logout_response = self.client.post(reverse("auth-logout"))
        self.assertEqual(logout_response.status_code, 200)

        self.client.credentials()
        current_user_after_logout_response = self.client.get(reverse("auth-current-user"))
        self.assertEqual(current_user_after_logout_response.status_code, 401)


class PasswordResetApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="reset_user",
            email="reset@example.com",
            password="OldStrongPass123",
        )

    def token_payload(self, token=None, uid=None, new_password="NewStrongPass123", confirm_password="NewStrongPass123"):
        return {
            "uid": uid or urlsafe_base64_encode(force_bytes(self.user.pk)),
            "token": token or default_token_generator.make_token(self.user),
            "new_password": new_password,
            "confirm_password": confirm_password,
        }

    @override_settings(DEBUG=True)
    def test_forgot_password_returns_generic_success_response(self):
        response = self.client.post(
            reverse("auth-forgot-password"),
            {"email": "reset@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertIn("reset_url", response.data)
        self.assertIn("/reset-password?uid=", response.data["reset_url"])

    @override_settings(DEBUG=True)
    def test_forgot_password_returns_generic_success_for_unknown_email(self):
        response = self.client.post(
            reverse("auth-forgot-password"),
            {"email": "missing@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.data)
        self.assertNotIn("reset_url", response.data)

    def test_valid_reset_token_changes_password_and_allows_login(self):
        response = self.client.post(
            reverse("auth-reset-password"),
            self.token_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass123"))

        login_response = self.client.post(
            reverse("auth-login"),
            {"username": "reset_user", "password": "NewStrongPass123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data)
        self.assertIn("refresh", login_response.data)

    def test_invalid_token_is_rejected(self):
        response = self.client.post(
            reverse("auth-reset-password"),
            self.token_payload(token="invalid-token"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("token", response.data)

    def test_password_mismatch_is_rejected(self):
        response = self.client.post(
            reverse("auth-reset-password"),
            self.token_payload(confirm_password="DifferentStrongPass123"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("confirm_password", response.data)

    def test_unknown_uid_is_rejected(self):
        response = self.client.post(
            reverse("auth-reset-password"),
            self.token_payload(uid="unknown-uid"),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("uid", response.data)
