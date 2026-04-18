from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from courses.models import Category, Course, Lesson, Module
from users.models import UserProfile
from .models import (
    Enrollment,
    EnrollmentRequest,
    ProgressRecord,
    Quiz,
    QuizChoice,
    QuizQuestion,
    QuizSubmission,
    Task,
    TaskSubmission,
)


class LearningAppSmokeTest(TestCase):
    def test_app_placeholder(self):
        self.assertTrue(True)


class EnrollmentApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.student = User.objects.create_user(
            username="student_enroll",
            email="student_enroll@example.com",
            password="StrongPass123",
        )
        self.teacher = User.objects.create_user(
            username="teacher_enroll",
            email="teacher_enroll@example.com",
            password="StrongPass123",
        )
        UserProfile.objects.update_or_create(
            user=self.student,
            defaults={"role": UserProfile.Role.STUDENT},
        )
        UserProfile.objects.update_or_create(
            user=self.teacher,
            defaults={"role": UserProfile.Role.TEACHER},
        )
        category = Category.objects.create(name="Speaking")
        self.course = Course.objects.create(
            category=category,
            title="Enrollment Course",
            description="A course for enrollment tests.",
            level="A1",
            is_published=True,
        )
        self.module = Module.objects.create(course=self.course, title="Basics", order=1)
        self.lesson = Lesson.objects.create(
            module=self.module,
            title="First lesson",
            youtube_url="https://www.youtube.com/watch?v=HAnw168huqA",
            order=1,
        )

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_student_can_request_enrollment_and_cannot_duplicate_pending_request(self):
        self.authenticate(self.student)
        response = self.client.post(reverse("enroll-course", args=[self.course.id]))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "request_created")
        self.assertEqual(EnrollmentRequest.objects.count(), 1)
        self.assertEqual(Enrollment.objects.count(), 0)

        duplicate_response = self.client.post(reverse("enroll-course", args=[self.course.id]))

        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(duplicate_response.data["status"], "request_pending")
        self.assertEqual(EnrollmentRequest.objects.count(), 1)
        self.assertEqual(Enrollment.objects.count(), 0)

    def test_teacher_can_approve_and_reject_enrollment_requests(self):
        self.course.teacher = self.teacher
        self.course.save(update_fields=["teacher"])
        enrollment_request = EnrollmentRequest.objects.create(student=self.student, course=self.course)
        self.authenticate(self.teacher)

        approve_response = self.client.post(
            reverse("teacher-update-enrollment-request", args=[enrollment_request.id, "approve"])
        )

        self.assertEqual(approve_response.status_code, 200)
        self.assertEqual(approve_response.data["status"], "approved")
        self.assertEqual(Enrollment.objects.filter(student=self.student, course=self.course).count(), 1)

        reject_response = self.client.post(
            reverse("teacher-update-enrollment-request", args=[enrollment_request.id, "reject"])
        )

        self.assertEqual(reject_response.status_code, 200)
        self.assertEqual(reject_response.data["status"], "rejected")
        self.assertFalse(Enrollment.objects.filter(student=self.student, course=self.course).exists())

    def test_teacher_can_view_student_progress_for_own_courses(self):
        self.course.teacher = self.teacher
        self.course.save(update_fields=["teacher"])
        Enrollment.objects.create(student=self.student, course=self.course)
        ProgressRecord.objects.create(student=self.student, lesson=self.lesson, is_completed=True)
        Lesson.objects.create(module=self.module, title="Second lesson", order=2)
        self.authenticate(self.teacher)

        response = self.client.get(reverse("teacher-student-progress"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["student_username"], self.student.username)
        self.assertEqual(response.data[0]["completed_lessons"], 1)
        self.assertEqual(response.data[0]["total_lessons"], 2)
        self.assertEqual(response.data[0]["percentage"], 50)

    def test_my_courses_returns_only_current_user_enrollments(self):
        other_student = User.objects.create_user(username="other_student", password="StrongPass123")
        Enrollment.objects.create(student=self.student, course=self.course)
        other_course = Course.objects.create(title="Other Course", is_published=True)
        Enrollment.objects.create(student=other_student, course=other_course)

        self.authenticate(self.student)
        response = self.client.get(reverse("my-courses"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["course"]["title"], "Enrollment Course")

    def test_teacher_cannot_enroll(self):
        self.authenticate(self.teacher)
        response = self.client.post(reverse("enroll-course", args=[self.course.id]))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "forbidden")

    def test_invalid_course_returns_not_found(self):
        self.authenticate(self.student)
        response = self.client.post(reverse("enroll-course", args=[9999]))

        self.assertEqual(response.status_code, 404)

    def test_student_can_complete_lesson_once_and_progress_is_calculated(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        Lesson.objects.create(module=self.module, title="Second lesson", order=2)
        self.authenticate(self.student)

        response = self.client.post(reverse("complete-lesson", args=[self.lesson.id]))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "completed")
        self.assertEqual(ProgressRecord.objects.count(), 1)

        duplicate_response = self.client.post(reverse("complete-lesson", args=[self.lesson.id]))

        self.assertEqual(duplicate_response.status_code, 200)
        self.assertEqual(duplicate_response.data["status"], "already_completed")
        self.assertEqual(ProgressRecord.objects.count(), 1)

        progress_response = self.client.get(reverse("progress-summary"))

        self.assertEqual(progress_response.status_code, 200)
        self.assertEqual(progress_response.data[0]["total_lessons"], 2)
        self.assertEqual(progress_response.data[0]["completed_lessons"], 1)
        self.assertEqual(progress_response.data[0]["percentage"], 50)

    def test_teacher_cannot_complete_lesson(self):
        Enrollment.objects.create(student=self.student, course=self.course)
        self.authenticate(self.teacher)

        response = self.client.post(reverse("complete-lesson", args=[self.lesson.id]))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "forbidden")

    def test_student_must_be_enrolled_to_complete_lesson(self):
        self.authenticate(self.student)

        response = self.client.post(reverse("complete-lesson", args=[self.lesson.id]))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data["status"], "not_enrolled")

    def create_quiz(self):
        quiz = Quiz.objects.create(lesson=self.lesson, title="Lesson Quiz")
        question_one = QuizQuestion.objects.create(quiz=quiz, text="Choose the greeting.", order=1)
        correct_one = QuizChoice.objects.create(question=question_one, text="Good morning", is_correct=True, order=1)
        QuizChoice.objects.create(question=question_one, text="Goodbye forever", is_correct=False, order=2)
        question_two = QuizQuestion.objects.create(quiz=quiz, text="Choose the correct sentence.", order=2)
        QuizChoice.objects.create(question=question_two, text="I from Astana.", is_correct=False, order=1)
        correct_two = QuizChoice.objects.create(question=question_two, text="I am from Astana.", is_correct=True, order=2)
        return quiz, correct_one, correct_two

    def test_enrolled_student_can_get_and_submit_quiz(self):
        quiz, correct_one, correct_two = self.create_quiz()
        Enrollment.objects.create(student=self.student, course=self.course)
        self.authenticate(self.student)

        quiz_response = self.client.get(reverse("lesson-quiz", args=[self.lesson.id]))
        self.assertEqual(quiz_response.status_code, 200)
        self.assertEqual(quiz_response.data["title"], "Lesson Quiz")
        self.assertEqual(len(quiz_response.data["questions"]), 2)

        submit_response = self.client.post(
            reverse("submit-quiz", args=[self.lesson.id]),
            {
                "answers": [
                    {"question_id": correct_one.question_id, "choice_id": correct_one.id},
                    {"question_id": correct_two.question_id, "choice_id": correct_two.id},
                ]
            },
            format="json",
        )

        self.assertEqual(submit_response.status_code, 201)
        self.assertEqual(submit_response.data["score"], 2)
        self.assertEqual(submit_response.data["total_questions"], 2)
        self.assertEqual(submit_response.data["percentage"], 100)
        self.assertEqual(QuizSubmission.objects.filter(quiz=quiz, student=self.student).count(), 1)

    def test_quiz_submit_requires_enrollment_and_student_role(self):
        self.create_quiz()

        self.authenticate(self.student)
        not_enrolled_response = self.client.post(
            reverse("submit-quiz", args=[self.lesson.id]),
            {"answers": []},
            format="json",
        )
        self.assertEqual(not_enrolled_response.status_code, 403)
        self.assertEqual(not_enrolled_response.data["status"], "not_enrolled")

        self.authenticate(self.teacher)
        teacher_response = self.client.post(
            reverse("submit-quiz", args=[self.lesson.id]),
            {"answers": []},
            format="json",
        )
        self.assertEqual(teacher_response.status_code, 403)
        self.assertEqual(teacher_response.data["status"], "forbidden")

    def test_enrolled_student_can_submit_and_update_task_answer(self):
        task = Task.objects.create(
            lesson=self.lesson,
            title="Write an answer",
            instructions="Write two sentences.",
        )
        Enrollment.objects.create(student=self.student, course=self.course)
        self.authenticate(self.student)

        task_response = self.client.get(reverse("lesson-task", args=[self.lesson.id]))
        self.assertEqual(task_response.status_code, 200)
        self.assertEqual(task_response.data["title"], "Write an answer")

        submit_response = self.client.post(
            reverse("submit-task", args=[self.lesson.id]),
            {"answer_text": "Hello. My name is Aida."},
            format="json",
        )
        self.assertEqual(submit_response.status_code, 201)
        self.assertEqual(submit_response.data["status"], "submitted")
        self.assertEqual(TaskSubmission.objects.filter(task=task, student=self.student).count(), 1)

        update_response = self.client.post(
            reverse("submit-task", args=[self.lesson.id]),
            {"answer_text": "Hello. My name is Aida. I live in Almaty."},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.data["status"], "updated")
        self.assertEqual(TaskSubmission.objects.filter(task=task, student=self.student).count(), 1)

    def test_task_submit_requires_answer_text(self):
        Task.objects.create(lesson=self.lesson, title="Write an answer", instructions="Write two sentences.")
        Enrollment.objects.create(student=self.student, course=self.course)
        self.authenticate(self.student)

        response = self.client.post(
            reverse("submit-task", args=[self.lesson.id]),
            {"answer_text": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["status"], "invalid")

    def test_teacher_can_create_quiz_question_choice_and_task(self):
        self.course.teacher = self.teacher
        self.course.save(update_fields=["teacher"])
        self.authenticate(self.teacher)

        quiz_response = self.client.post(
            reverse("teacher-create-quiz"),
            {"lesson": self.lesson.id, "title": "Teacher Quiz"},
            format="json",
        )
        self.assertEqual(quiz_response.status_code, 201)

        question_response = self.client.post(
            reverse("teacher-create-question"),
            {"quiz": quiz_response.data["id"], "text": "Choose the greeting.", "order": 1},
            format="json",
        )
        self.assertEqual(question_response.status_code, 201)

        choice_response = self.client.post(
            reverse("teacher-create-choice"),
            {
                "question": question_response.data["id"],
                "text": "Good morning",
                "is_correct": True,
                "order": 1,
            },
            format="json",
        )
        self.assertEqual(choice_response.status_code, 201)
        self.assertTrue(QuizChoice.objects.get(id=choice_response.data["id"]).is_correct)

        task_response = self.client.post(
            reverse("teacher-create-task"),
            {
                "lesson": self.lesson.id,
                "title": "Teacher Task",
                "instructions": "Write two sentences.",
            },
            format="json",
        )
        self.assertEqual(task_response.status_code, 201)
        self.assertEqual(Task.objects.get(id=task_response.data["id"]).lesson, self.lesson)

    def test_teacher_can_view_only_own_quiz_and_task_submissions(self):
        self.course.teacher = self.teacher
        self.course.save(update_fields=["teacher"])
        other_teacher = User.objects.create_user(username="other_teacher", password="StrongPass123")
        UserProfile.objects.update_or_create(
            user=other_teacher,
            defaults={"role": UserProfile.Role.TEACHER},
        )
        other_course = Course.objects.create(title="Other Teacher Course", teacher=other_teacher, is_published=True)
        other_module = Module.objects.create(course=other_course, title="Other Module")
        other_lesson = Lesson.objects.create(module=other_module, title="Other Lesson")

        quiz, correct_one, _ = self.create_quiz()
        task = Task.objects.create(lesson=self.lesson, title="Write an answer")
        Enrollment.objects.create(student=self.student, course=self.course)
        QuizSubmission.objects.create(
            student=self.student,
            quiz=quiz,
            selected_answers={str(correct_one.question_id): correct_one.id},
            score=1,
            total_questions=2,
        )
        TaskSubmission.objects.create(student=self.student, task=task, answer_text="My answer.")

        other_quiz = Quiz.objects.create(lesson=other_lesson, title="Other Quiz")
        QuizSubmission.objects.create(student=self.student, quiz=other_quiz, score=0, total_questions=0)
        other_task = Task.objects.create(lesson=other_lesson, title="Other Task")
        TaskSubmission.objects.create(student=self.student, task=other_task, answer_text="Other answer.")

        self.authenticate(self.teacher)

        quiz_response = self.client.get(reverse("teacher-quiz-submissions"))
        self.assertEqual(quiz_response.status_code, 200)
        self.assertEqual(len(quiz_response.data), 1)
        self.assertEqual(quiz_response.data[0]["quiz_title"], "Lesson Quiz")
        self.assertEqual(quiz_response.data[0]["student_username"], self.student.username)

        task_response = self.client.get(reverse("teacher-task-submissions"))
        self.assertEqual(task_response.status_code, 200)
        self.assertEqual(len(task_response.data), 1)
        self.assertEqual(task_response.data[0]["task_title"], "Write an answer")
        self.assertEqual(task_response.data[0]["student_username"], self.student.username)

    def test_student_cannot_use_teacher_learning_endpoints(self):
        self.authenticate(self.student)
        response = self.client.post(
            reverse("teacher-create-quiz"),
            {"lesson": self.lesson.id, "title": "Blocked Quiz"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_create_task_for_another_teachers_lesson(self):
        self.authenticate(self.teacher)
        response = self.client.post(
            reverse("teacher-create-task"),
            {
                "lesson": self.lesson.id,
                "title": "Blocked Task",
                "instructions": "Should not work.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
