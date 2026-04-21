from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import UserProfile
from .models import Booking, LessonSlot


class BookingAppSmokeTest(TestCase):
    def test_app_placeholder(self):
        self.assertTrue(True)


class BookingApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(username="booking_teacher", password="StrongPass123")
        self.student = User.objects.create_user(username="booking_student", password="StrongPass123")
        UserProfile.objects.update_or_create(
            user=self.teacher,
            defaults={"role": UserProfile.Role.TEACHER},
        )
        UserProfile.objects.update_or_create(
            user=self.student,
            defaults={"role": UserProfile.Role.STUDENT},
        )
        self.starts_at = timezone.now() + timedelta(days=1)
        self.ends_at = self.starts_at + timedelta(hours=1)

    def authenticate(self, user):
        access = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_teacher_can_create_slot_and_view_own_slots(self):
        self.authenticate(self.teacher)
        response = self.client.post(
            reverse("teacher-create-slot"),
            {
                "starts_at": self.starts_at.isoformat(),
                "ends_at": self.ends_at.isoformat(),
                "meeting_url": "https://meet.google.com/test-slot",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "slot_created")
        self.assertEqual(LessonSlot.objects.get(id=response.data["slot"]["id"]).teacher, self.teacher)
        self.assertEqual(response.data["slot"]["meeting_url"], "https://meet.google.com/test-slot")

        slots_response = self.client.get(reverse("teacher-my-slots"))
        self.assertEqual(slots_response.status_code, 200)
        self.assertEqual(len(slots_response.data), 1)

    def test_teacher_can_delete_own_unbooked_slot(self):
        slot = LessonSlot.objects.create(
            teacher=self.teacher,
            starts_at=self.starts_at,
            ends_at=self.ends_at,
        )
        self.authenticate(self.teacher)

        response = self.client.delete(reverse("teacher-delete-slot", args=[slot.id]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "slot_deleted")
        self.assertFalse(LessonSlot.objects.filter(id=slot.id).exists())

    def test_student_cannot_create_slot(self):
        self.authenticate(self.student)
        response = self.client.post(
            reverse("teacher-create-slot"),
            {
                "starts_at": self.starts_at.isoformat(),
                "ends_at": self.ends_at.isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_student_can_book_slot_and_cannot_double_book(self):
        slot = LessonSlot.objects.create(
            teacher=self.teacher,
            starts_at=self.starts_at,
            ends_at=self.ends_at,
        )
        self.authenticate(self.student)

        available_response = self.client.get(reverse("available-slots"))
        self.assertEqual(available_response.status_code, 200)
        self.assertEqual(len(available_response.data), 1)

        book_response = self.client.post(reverse("book-slot", args=[slot.id]))
        self.assertEqual(book_response.status_code, 201)
        self.assertEqual(book_response.data["status"], "slot_booked")
        self.assertEqual(Booking.objects.count(), 1)

        duplicate_response = self.client.post(reverse("book-slot", args=[slot.id]))
        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(duplicate_response.data["status"], "already_booked")
        self.assertEqual(Booking.objects.count(), 1)

        my_bookings_response = self.client.get(reverse("student-my-bookings"))
        self.assertEqual(my_bookings_response.status_code, 200)
        self.assertEqual(len(my_bookings_response.data), 1)

    def test_teacher_cannot_book_slot_as_student(self):
        slot = LessonSlot.objects.create(
            teacher=self.teacher,
            starts_at=self.starts_at,
            ends_at=self.ends_at,
        )
        self.authenticate(self.teacher)

        response = self.client.post(reverse("book-slot", args=[slot.id]))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "forbidden")

    def test_teacher_cannot_delete_booked_slot(self):
        slot = LessonSlot.objects.create(
            teacher=self.teacher,
            starts_at=self.starts_at,
            ends_at=self.ends_at,
            is_available=False,
        )
        Booking.objects.create(slot=slot, student=self.student)
        self.authenticate(self.teacher)

        response = self.client.delete(reverse("teacher-delete-slot", args=[slot.id]))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "cannot_delete_booked_slot")
        self.assertTrue(LessonSlot.objects.filter(id=slot.id).exists())

    def test_invalid_slot_returns_not_found(self):
        self.authenticate(self.student)
        response = self.client.post(reverse("book-slot", args=[9999]))

        self.assertEqual(response.status_code, 404)
