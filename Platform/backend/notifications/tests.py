from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models import Booking, LessonSlot
from courses.models import Course, Lesson, Module
from learning.models import Enrollment, Task, TaskSubmission
from users.models import UserProfile
from .models import Notification


class NotificationApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(username="notify_teacher", password="StrongPass123")
        self.student = User.objects.create_user(username="notify_student", password="StrongPass123")
        self.other_user = User.objects.create_user(username="notify_other", password="StrongPass123")
        UserProfile.objects.update_or_create(user=self.teacher, defaults={"role": UserProfile.Role.TEACHER})
        UserProfile.objects.update_or_create(user=self.student, defaults={"role": UserProfile.Role.STUDENT})
        UserProfile.objects.update_or_create(user=self.other_user, defaults={"role": UserProfile.Role.STUDENT})

        self.course = Course.objects.create(
            teacher=self.teacher,
            title="Notification Course",
            description="Course for notification tests.",
            is_published=True,
        )
        self.module = Module.objects.create(course=self.course, title="Module")
        self.lesson = Lesson.objects.create(module=self.module, title="Lesson")
        self.task = Task.objects.create(lesson=self.lesson, title="Writing task")
        Enrollment.objects.create(student=self.student, course=self.course)

    def authenticate(self, user):
        access = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_student_booking_creates_teacher_notification(self):
        starts_at = timezone.now() + timedelta(days=1)
        slot = LessonSlot.objects.create(
            teacher=self.teacher,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=1),
        )
        self.authenticate(self.student)

        response = self.client.post(reverse("book-slot", args=[slot.id]))

        self.assertEqual(response.status_code, 201)
        notification = Notification.objects.get(recipient=self.teacher, type=Notification.Type.BOOKING_CREATED)
        self.assertIn(self.student.username, notification.message)
        self.assertEqual(notification.metadata["slot_id"], slot.id)

    def test_student_task_submit_creates_teacher_notification(self):
        self.authenticate(self.student)

        response = self.client.post(
            reverse("submit-task", args=[self.lesson.id]),
            {"answer_text": "This is my written answer."},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        notification = Notification.objects.get(recipient=self.teacher, type=Notification.Type.TASK_SUBMITTED)
        self.assertEqual(notification.metadata["task_id"], self.task.id)
        self.assertIn(self.student.username, notification.message)

    def test_teacher_review_creates_student_notification(self):
        submission = TaskSubmission.objects.create(
            student=self.student,
            task=self.task,
            answer_text="Please review my answer.",
        )
        self.authenticate(self.teacher)

        response = self.client.post(
            reverse("teacher-review-task-submission", args=[submission.id]),
            {"score": 90, "teacher_feedback": "Strong answer."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        notification = Notification.objects.get(recipient=self.student, type=Notification.Type.TASK_REVIEWED)
        self.assertEqual(notification.metadata["submission_id"], submission.id)
        self.assertEqual(notification.metadata["score"], 90)

    def test_notification_api_returns_only_current_users_notifications(self):
        own = Notification.objects.create(
            recipient=self.student,
            title="Own notification",
            message="Visible",
            type=Notification.Type.TASK_REVIEWED,
        )
        Notification.objects.create(
            recipient=self.other_user,
            title="Other notification",
            message="Hidden",
            type=Notification.Type.TASK_REVIEWED,
        )
        self.authenticate(self.student)

        list_response = self.client.get(reverse("notification-list"))
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["id"], own.id)

        count_response = self.client.get(reverse("notification-unread-count"))
        self.assertEqual(count_response.status_code, 200)
        self.assertEqual(count_response.data["unread_count"], 1)

        mark_response = self.client.post(reverse("notification-mark-read", args=[own.id]))
        self.assertEqual(mark_response.status_code, 200)
        own.refresh_from_db()
        self.assertTrue(own.is_read)

    def test_user_cannot_modify_another_users_notification(self):
        other_notification = Notification.objects.create(
            recipient=self.other_user,
            title="Other notification",
            message="Hidden",
            type=Notification.Type.TASK_REVIEWED,
        )
        self.authenticate(self.student)

        mark_response = self.client.post(reverse("notification-mark-read", args=[other_notification.id]))
        delete_response = self.client.delete(reverse("notification-delete", args=[other_notification.id]))

        self.assertEqual(mark_response.status_code, 404)
        self.assertEqual(delete_response.status_code, 404)
        self.assertTrue(Notification.objects.filter(id=other_notification.id).exists())

    def test_mark_all_read_and_delete_own_notification(self):
        first = Notification.objects.create(
            recipient=self.student,
            title="First",
            message="Visible",
            type=Notification.Type.TASK_REVIEWED,
        )
        Notification.objects.create(
            recipient=self.student,
            title="Second",
            message="Visible",
            type=Notification.Type.TASK_REVIEWED,
        )
        self.authenticate(self.student)

        mark_all_response = self.client.post(reverse("notification-mark-all-read"))
        self.assertEqual(mark_all_response.status_code, 200)
        self.assertEqual(mark_all_response.data["updated_count"], 2)
        self.assertEqual(Notification.objects.filter(recipient=self.student, is_read=False).count(), 0)

        delete_response = self.client.delete(reverse("notification-delete", args=[first.id]))
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Notification.objects.filter(id=first.id).exists())
