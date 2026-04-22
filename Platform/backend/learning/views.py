from django.db.models import Case, F, IntegerField, Value, When
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson
from notifications.models import Notification
from notifications.services import create_notification
from users.models import UserProfile
from users.permissions import IsTeacher
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
from .serializers import (
    CourseProgressSerializer,
    EnrollmentRequestSerializer,
    EnrollmentSerializer,
    ProgressRecordSerializer,
    QuizAttemptSerializer,
    QuizChoiceSerializer,
    QuizQuestionSerializer,
    QuizSerializer,
    QuizSubmissionSerializer,
    QuizWithAttemptsSerializer,
    TaskAttemptSerializer,
    TaskSerializer,
    TaskSubmissionSerializer,
    TaskWithAttemptsSerializer,
    TeacherQuizChoiceCreateSerializer,
    TeacherQuizChoiceUpdateSerializer,
    TeacherQuizCreateSerializer,
    TeacherQuizUpdateSerializer,
    TeacherQuizQuestionCreateSerializer,
    TeacherQuizQuestionUpdateSerializer,
    TeacherStudentProgressSerializer,
    TeacherTaskCreateSerializer,
    TeacherTaskUpdateSerializer,
    TeacherTaskSubmissionReviewSerializer,
)


def require_student_enrolled(user, lesson):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.role != UserProfile.Role.STUDENT:
        return Response(
            {
                "status": "forbidden",
                "message": "Only student users can submit lesson activities.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    is_enrolled = Enrollment.objects.filter(
        student=user,
        course=lesson.module.course,
    ).exists()
    if not is_enrolled:
        return Response(
            {
                "status": "not_enrolled",
                "message": "Enroll in this course before submitting lesson activities.",
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    return None


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return (
            Enrollment.objects.filter(student=self.request.user)
            .select_related("student", "course", "course__category", "course__teacher")
            .prefetch_related("course__modules__lessons")
            .order_by("-created_at")
        )


class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = (
            Enrollment.objects.filter(student=request.user)
            .select_related("student", "course", "course__category", "course__teacher")
            .prefetch_related("course__modules__lessons")
            .order_by("-created_at")
        )
        return Response(EnrollmentSerializer(enrollments, many=True).data)


class MyTaskSubmissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.role != UserProfile.Role.STUDENT:
            return Response(
                {
                    "status": "forbidden",
                    "message": "Only student users can view their task submissions here.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        submissions = (
            TaskSubmission.objects.filter(student=request.user)
            .select_related("task", "task__lesson", "task__lesson__module", "task__lesson__module__course")
            .order_by("-updated_at")
        )
        return Response(TaskSubmissionSerializer(submissions, many=True).data)


class MyEnrollmentRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.role != UserProfile.Role.STUDENT:
            return Response(
                {
                    "status": "forbidden",
                    "message": "Only student users can view their enrollment requests here.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        enrollment_requests = (
            EnrollmentRequest.objects.filter(student=request.user)
            .select_related("student", "course", "course__category", "course__teacher")
            .prefetch_related("course__modules__lessons")
            .order_by("-updated_at")
        )
        return Response(EnrollmentRequestSerializer(enrollment_requests, many=True).data)


class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.role != UserProfile.Role.STUDENT:
            return Response(
                {
                    "status": "forbidden",
                    "message": "Only student users can request enrollment in courses.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        course = get_object_or_404(Course, id=course_id, is_published=True)
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course,
        ).first()

        if enrollment:
            return Response(
                {
                    "status": "already_enrolled",
                    "message": "You are already enrolled in this course.",
                    "enrollment": EnrollmentSerializer(enrollment).data,
                },
                status=status.HTTP_200_OK,
            )

        enrollment_request, created = EnrollmentRequest.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={"status": EnrollmentRequest.Status.PENDING},
        )

        if not created and enrollment_request.status == EnrollmentRequest.Status.PENDING:
            return Response(
                {
                    "status": "request_pending",
                    "message": "Your enrollment request is already waiting for teacher approval.",
                    "request": EnrollmentRequestSerializer(enrollment_request).data,
                },
                status=status.HTTP_200_OK,
            )

        if not created and enrollment_request.status == EnrollmentRequest.Status.REJECTED:
            enrollment_request.status = EnrollmentRequest.Status.PENDING
            enrollment_request.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "status": "request_created",
                "message": "Enrollment request sent. The course will appear in My Courses after teacher approval.",
                "request": EnrollmentRequestSerializer(enrollment_request).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TeacherEnrollmentRequestsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        enrollment_requests = (
            EnrollmentRequest.objects.filter(course__teacher=request.user)
            .annotate(
                status_order=Case(
                    When(status=EnrollmentRequest.Status.PENDING, then=Value(0)),
                    When(status=EnrollmentRequest.Status.APPROVED, then=Value(1)),
                    When(status=EnrollmentRequest.Status.REJECTED, then=Value(2)),
                    default=Value(3),
                    output_field=IntegerField(),
                )
            )
            .select_related("student", "course", "course__category", "course__teacher")
            .prefetch_related("course__modules__lessons")
            .order_by("status_order", "-updated_at")
        )
        return Response(EnrollmentRequestSerializer(enrollment_requests, many=True).data)


class TeacherUpdateEnrollmentRequestView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request, request_id, action):
        enrollment_request = get_object_or_404(
            EnrollmentRequest.objects.select_related("student", "course", "course__teacher"),
            id=request_id,
            course__teacher=request.user,
        )

        if action not in ["approve", "reject"]:
            return Response(
                {
                    "status": "invalid_action",
                    "message": "Action must be approve or reject.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "approve":
            enrollment_request.status = EnrollmentRequest.Status.APPROVED
            enrollment_request.save(update_fields=["status", "updated_at"])
            enrollment, _ = Enrollment.objects.get_or_create(
                student=enrollment_request.student,
                course=enrollment_request.course,
            )
            return Response(
                {
                    "status": "approved",
                    "message": "Enrollment request approved.",
                    "request": EnrollmentRequestSerializer(enrollment_request).data,
                    "enrollment": EnrollmentSerializer(enrollment).data,
                }
            )

        enrollment_request.status = EnrollmentRequest.Status.REJECTED
        enrollment_request.save(update_fields=["status", "updated_at"])
        Enrollment.objects.filter(
            student=enrollment_request.student,
            course=enrollment_request.course,
        ).delete()
        return Response(
            {
                "status": "rejected",
                "message": "Enrollment request rejected.",
                "request": EnrollmentRequestSerializer(enrollment_request).data,
            }
        )


class TeacherStudentProgressView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        enrollments = (
            Enrollment.objects.filter(course__teacher=request.user)
            .select_related("student", "course")
            .prefetch_related("course__modules__lessons")
            .order_by("course__title", "student__username")
        )

        progress_items = []
        for enrollment in enrollments:
            lesson_ids = [
                lesson.id
                for module in enrollment.course.modules.all()
                for lesson in module.lessons.all()
            ]
            total_lessons = len(lesson_ids)
            completed_lessons = ProgressRecord.objects.filter(
                student=enrollment.student,
                lesson_id__in=lesson_ids,
                is_completed=True,
            ).count()
            percentage = round((completed_lessons / total_lessons) * 100) if total_lessons else 0

            progress_items.append(
                {
                    "enrollment_id": enrollment.id,
                    "student_username": enrollment.student.username,
                    "course_id": enrollment.course.id,
                    "course_title": enrollment.course.title,
                    "completed_lessons": completed_lessons,
                    "total_lessons": total_lessons,
                    "percentage": percentage,
                }
            )

        return Response(TeacherStudentProgressSerializer(progress_items, many=True).data)


class CompleteLessonView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if profile.role != UserProfile.Role.STUDENT:
            return Response(
                {
                    "status": "forbidden",
                    "message": "Only student users can mark lessons as completed.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        lesson = get_object_or_404(
            Lesson.objects.select_related("module", "module__course"),
            id=lesson_id,
        )
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=lesson.module.course,
        ).exists()

        if not is_enrolled:
            return Response(
                {
                    "status": "not_enrolled",
                    "message": "Enroll in this course before completing lessons.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        record, created = ProgressRecord.objects.get_or_create(
            student=request.user,
            lesson=lesson,
            defaults={"is_completed": True},
        )

        if not created and record.is_completed:
            return Response(
                {
                    "status": "already_completed",
                    "message": "This lesson is already marked as completed.",
                    "progress": ProgressRecordSerializer(record).data,
                },
                status=status.HTTP_200_OK,
            )

        if not record.is_completed:
            record.is_completed = True
            record.save(update_fields=["is_completed", "updated_at"])

        return Response(
            {
                "status": "completed",
                "message": "Lesson marked as completed.",
                "progress": ProgressRecordSerializer(record).data,
            },
            status=status.HTTP_201_CREATED,
        )


def _compute_course_progress(user, course):
    """Return a progress dict for one course and one student."""
    lesson_ids = [
        lesson.id
        for module in course.modules.all()
        for lesson in module.lessons.all()
    ]
    total_lessons = len(lesson_ids)

    completed_lessons = ProgressRecord.objects.filter(
        student=user,
        lesson_id__in=lesson_ids,
        is_completed=True,
    ).count()

    quiz_ids = list(Quiz.objects.filter(lesson_id__in=lesson_ids).values_list("id", flat=True))
    task_ids = list(Task.objects.filter(lesson_id__in=lesson_ids).values_list("id", flat=True))
    total_tasks = len(quiz_ids) + len(task_ids)

    completed_quizzes_count = (
        QuizSubmission.objects.filter(
            student=user,
            quiz_id__in=quiz_ids,
            total_questions__gt=0,
        )
        .filter(score=F("total_questions"))
        .values("quiz_id")
        .distinct()
        .count()
    ) if quiz_ids else 0

    completed_tasks_count = (
        TaskSubmission.objects.filter(
            student=user,
            task_id__in=task_ids,
            passed=True,
        )
        .values("task_id")
        .distinct()
        .count()
    ) if task_ids else 0

    completed_tasks = completed_quizzes_count + completed_tasks_count

    if total_lessons == 0 and total_tasks == 0:
        watched_percent = 0
        tasks_percent = 0
        overall_progress = 0
    elif total_tasks == 0:
        watched_percent = round((completed_lessons / total_lessons) * 100)
        tasks_percent = 0
        overall_progress = watched_percent
    elif total_lessons == 0:
        watched_percent = 0
        tasks_percent = round((completed_tasks / total_tasks) * 100)
        overall_progress = tasks_percent
    else:
        watched_percent = round((completed_lessons / total_lessons) * 100)
        tasks_percent = round((completed_tasks / total_tasks) * 100)
        overall_progress = round(
            (completed_lessons / total_lessons) * 50
            + (completed_tasks / total_tasks) * 50
        )

    return {
        "course_id": course.id,
        "course_title": course.title,
        "total_lessons": total_lessons,
        "completed_lessons": completed_lessons,
        "watched_percent": watched_percent,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "tasks_percent": tasks_percent,
        "overall_progress": overall_progress,
        "percentage": overall_progress,
    }


class ProgressSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = (
            Enrollment.objects.filter(student=request.user)
            .select_related("course")
            .prefetch_related("course__modules__lessons")
            .order_by("-created_at")
        )

        progress_items = [
            _compute_course_progress(request.user, enrollment.course)
            for enrollment in enrollments
        ]

        serializer = CourseProgressSerializer(progress_items, many=True)
        return Response(serializer.data)


class CourseDetailProgressView(APIView):
    """Per-course progress breakdown: lessons + assignments + overall."""

    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(
            Course.objects.prefetch_related("modules__lessons"),
            id=course_id,
        )
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response({"detail": "Not enrolled."}, status=status.HTTP_403_FORBIDDEN)

        data = _compute_course_progress(request.user, course)
        serializer = CourseProgressSerializer(data)
        return Response(serializer.data)


class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.select_related("lesson")
    serializer_class = TaskSerializer


class LessonQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson.objects.select_related("module", "module__course"), id=lesson_id)
        permission_error = require_student_enrolled(request.user, lesson)
        if permission_error:
            return permission_error

        quiz = get_object_or_404(
            Quiz.objects.prefetch_related("questions__choices"),
            lesson=lesson,
        )
        return Response(QuizSerializer(quiz).data)


class SubmitQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson.objects.select_related("module", "module__course"), id=lesson_id)
        permission_error = require_student_enrolled(request.user, lesson)
        if permission_error:
            return permission_error

        quiz = get_object_or_404(
            Quiz.objects.prefetch_related("questions__choices"),
            lesson=lesson,
        )
        answers = request.data.get("answers", [])
        if not isinstance(answers, list):
            return Response(
                {
                    "status": "invalid",
                    "message": "Answers must be a list of question_id and choice_id objects.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        answer_map = {}
        for answer in answers:
            question_id = answer.get("question_id")
            choice_id = answer.get("choice_id")
            if question_id is not None and choice_id is not None:
                answer_map[int(question_id)] = int(choice_id)

        questions = list(quiz.questions.all())
        score = 0
        for question in questions:
            selected_choice_id = answer_map.get(question.id)
            if selected_choice_id is None:
                continue

            is_correct = QuizChoice.objects.filter(
                id=selected_choice_id,
                question=question,
                is_correct=True,
            ).exists()
            if is_correct:
                score += 1

        submission = QuizSubmission.objects.create(
            student=request.user,
            quiz=quiz,
            selected_answers={str(key): value for key, value in answer_map.items()},
            score=score,
            total_questions=len(questions),
        )

        return Response(
            {
                "status": "submitted",
                "message": "Quiz submitted successfully.",
                "score": score,
                "total_questions": len(questions),
                "percentage": round((score / len(questions)) * 100) if questions else 0,
                "submission": QuizSubmissionSerializer(submission).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LessonTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson.objects.select_related("module", "module__course"), id=lesson_id)
        permission_error = require_student_enrolled(request.user, lesson)
        if permission_error:
            return permission_error

        task = get_object_or_404(Task.objects.select_related("lesson"), lesson=lesson)
        return Response(TaskSerializer(task).data)


class SubmitTaskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(
            Lesson.objects.select_related("module", "module__course", "module__course__teacher"),
            id=lesson_id,
        )
        permission_error = require_student_enrolled(request.user, lesson)
        if permission_error:
            return permission_error

        task = get_object_or_404(Task.objects.select_related("lesson"), lesson=lesson)
        answer_text = request.data.get("answer_text", "").strip()
        if not answer_text:
            return Response(
                {
                    "status": "invalid",
                    "message": "Task answer text is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Always create a new attempt
        latest = TaskSubmission.objects.filter(task=task, student=request.user).order_by("-submitted_at").first()
        if latest and latest.status == TaskSubmission.Status.SUBMITTED:
            return Response(
                {"status": "pending_review", "message": "Your previous answer is awaiting teacher review."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if latest and latest.passed:
            return Response(
                {"status": "already_passed", "message": "You have already passed this task."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission = TaskSubmission.objects.create(
            student=request.user,
            task=task,
            answer_text=answer_text,
            status=TaskSubmission.Status.SUBMITTED,
        )
        created = True
        create_notification(
            recipient=lesson.module.course.teacher,
            title="Written task submitted",
            message=f"{request.user.username} submitted '{task.title}' in {lesson.title}.",
            notification_type=Notification.Type.TASK_SUBMITTED,
            metadata={
                "task_id": task.id,
                "submission_id": submission.id,
                "lesson_id": lesson.id,
                "course_id": lesson.module.course_id,
                "student_username": request.user.username,
                "action": "created" if created else "updated",
            },
        )

        return Response(
            {
                "status": "submitted" if created else "updated",
                "message": "Task answer submitted successfully." if created else "Task answer updated successfully.",
                "submission": TaskSubmissionSerializer(submission).data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TeacherQuizCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherQuizCreateSerializer


class TeacherQuizQuestionCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherQuizQuestionCreateSerializer


class TeacherQuizChoiceCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherQuizChoiceCreateSerializer


class TeacherTaskCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherTaskCreateSerializer


class TeacherOwnedLearningContentMixin:
    permission_classes = [IsAuthenticated, IsTeacher]
    ownership_error_message = "You can manage only your own content."
    delete_success_message = "Content deleted successfully."

    def check_owner(self, obj):
        raise NotImplementedError

    def get_object(self):
        obj = super().get_object()
        if not self.check_owner(obj):
            raise PermissionDenied(self.ownership_error_message)
        return obj

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response({"message": self.delete_success_message})


class TeacherQuizDetailView(TeacherOwnedLearningContentMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.select_related("lesson", "lesson__module", "lesson__module__course")
    serializer_class = TeacherQuizUpdateSerializer
    ownership_error_message = "You can edit or delete only quizzes from your own courses."
    delete_success_message = "Quiz deleted successfully."
    http_method_names = ["patch", "delete", "options"]

    def check_owner(self, obj):
        return obj.lesson.module.course.teacher_id == self.request.user.id


class TeacherQuizQuestionDetailView(TeacherOwnedLearningContentMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = QuizQuestion.objects.select_related("quiz", "quiz__lesson", "quiz__lesson__module", "quiz__lesson__module__course")
    serializer_class = TeacherQuizQuestionUpdateSerializer
    ownership_error_message = "You can edit or delete only questions from your own quizzes."
    delete_success_message = "Question deleted successfully."
    http_method_names = ["patch", "delete", "options"]

    def check_owner(self, obj):
        return obj.quiz.lesson.module.course.teacher_id == self.request.user.id


class TeacherQuizChoiceDetailView(TeacherOwnedLearningContentMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = QuizChoice.objects.select_related(
        "question",
        "question__quiz",
        "question__quiz__lesson",
        "question__quiz__lesson__module",
        "question__quiz__lesson__module__course",
    )
    serializer_class = TeacherQuizChoiceUpdateSerializer
    ownership_error_message = "You can edit or delete only choices from your own questions."
    delete_success_message = "Choice deleted successfully."
    http_method_names = ["patch", "delete", "options"]

    def check_owner(self, obj):
        return obj.question.quiz.lesson.module.course.teacher_id == self.request.user.id


class TeacherTaskDetailView(TeacherOwnedLearningContentMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.select_related("lesson", "lesson__module", "lesson__module__course")
    serializer_class = TeacherTaskUpdateSerializer
    ownership_error_message = "You can edit or delete only written tasks from your own courses."
    delete_success_message = "Written task deleted successfully."
    http_method_names = ["patch", "delete", "options"]

    def check_owner(self, obj):
        return obj.lesson.module.course.teacher_id == self.request.user.id


class TeacherMyQuizzesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = QuizSerializer

    def get_queryset(self):
        return (
            Quiz.objects.filter(lesson__module__course__teacher=self.request.user)
            .select_related("lesson", "lesson__module", "lesson__module__course")
            .prefetch_related("questions__choices")
            .order_by("lesson__module__course__title", "lesson__module__order", "lesson__order", "id")
        )


class TeacherMyQuestionsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = QuizQuestionSerializer

    def get_queryset(self):
        return (
            QuizQuestion.objects.filter(quiz__lesson__module__course__teacher=self.request.user)
            .select_related("quiz", "quiz__lesson", "quiz__lesson__module", "quiz__lesson__module__course")
            .prefetch_related("choices")
            .order_by("quiz__lesson__module__course__title", "quiz__lesson__order", "quiz__title", "order", "id")
        )


class TeacherMyChoicesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = QuizChoiceSerializer

    def get_queryset(self):
        return (
            QuizChoice.objects.filter(question__quiz__lesson__module__course__teacher=self.request.user)
            .select_related(
                "question",
                "question__quiz",
                "question__quiz__lesson",
                "question__quiz__lesson__module",
                "question__quiz__lesson__module__course",
            )
            .order_by("question__quiz__lesson__module__course__title", "question__quiz__title", "question__order", "order", "id")
        )


class TeacherMyTasksView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return (
            Task.objects.filter(lesson__module__course__teacher=self.request.user)
            .select_related("lesson", "lesson__module", "lesson__module__course")
            .order_by("lesson__module__course__title", "lesson__module__order", "lesson__order", "id")
        )


class TeacherQuizSubmissionsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        submissions = (
            QuizSubmission.objects.filter(quiz__lesson__module__course__teacher=request.user)
            .select_related("student", "quiz", "quiz__lesson", "quiz__lesson__module", "quiz__lesson__module__course")
            .order_by("-submitted_at")
        )
        return Response(QuizSubmissionSerializer(submissions, many=True).data)


class TeacherTaskSubmissionsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        submissions = (
            TaskSubmission.objects.filter(task__lesson__module__course__teacher=request.user)
            .select_related("student", "task", "task__lesson", "task__lesson__module", "task__lesson__module__course")
            .order_by("-updated_at")
        )
        return Response(TaskSubmissionSerializer(submissions, many=True).data)


class TeacherReviewTaskSubmissionView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    passing_score = 60

    def post(self, request, submission_id):
        submission = get_object_or_404(
            TaskSubmission.objects.select_related(
                "student",
                "task",
                "task__lesson",
                "task__lesson__module",
                "task__lesson__module__course",
            ),
            id=submission_id,
            task__lesson__module__course__teacher=request.user,
        )

        serializer = TeacherTaskSubmissionReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        score = serializer.validated_data["score"]
        passed = serializer.validated_data.get("passed", score >= self.passing_score)

        submission.score = score
        submission.teacher_feedback = serializer.validated_data.get("teacher_feedback", "")
        submission.passed = passed
        submission.status = TaskSubmission.Status.REVIEWED
        submission.reviewed_at = timezone.now()
        submission.save(update_fields=["score", "teacher_feedback", "passed", "status", "reviewed_at", "updated_at"])

        create_notification(
            recipient=submission.student,
            title="Written task reviewed",
            message=f"Your task '{submission.task.title}' was reviewed. Score: {submission.score}/100.",
            notification_type=Notification.Type.TASK_REVIEWED,
            metadata={
                "task_id": submission.task_id,
                "submission_id": submission.id,
                "lesson_id": submission.task.lesson_id,
                "course_id": submission.task.lesson.module.course_id,
                "score": submission.score,
            },
        )

        return Response(
            {
                "status": "reviewed",
                "message": "Task submission reviewed successfully.",
                "submission": TaskSubmissionSerializer(submission).data,
            }
        )


class ProgressRecordViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgressRecordSerializer

    def get_queryset(self):
        return ProgressRecord.objects.filter(student=self.request.user).select_related("student", "lesson")


# ── Student attempt views ──────────────────────────────────────────────────────

class QuizDetailView(APIView):
    """Quiz with questions + this student's attempt history."""
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related("questions__choices").select_related("lesson__module__course"),
            id=quiz_id,
        )
        error = require_student_enrolled(request.user, quiz.lesson)
        if error:
            return error
        return Response(QuizWithAttemptsSerializer(quiz, context={"request": request}).data)


class SubmitQuizByIdView(APIView):
    """Submit a new quiz attempt by quiz ID."""
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):
        quiz = get_object_or_404(
            Quiz.objects.prefetch_related("questions__choices").select_related("lesson__module__course"),
            id=quiz_id,
        )
        error = require_student_enrolled(request.user, quiz.lesson)
        if error:
            return error

        already_passed = QuizSubmission.objects.filter(
            quiz=quiz, student=request.user, score=F("total_questions")
        ).exclude(total_questions=0).exists()
        if already_passed:
            return Response(
                {"status": "already_passed", "message": "You already achieved 100% on this quiz."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answers = request.data.get("answers", [])
        if not isinstance(answers, list):
            return Response(
                {"status": "invalid", "message": "Answers must be a list of {question_id, choice_id}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        answer_map = {}
        for ans in answers:
            qid = ans.get("question_id")
            cid = ans.get("choice_id")
            if qid is not None and cid is not None:
                answer_map[int(qid)] = int(cid)

        questions = list(quiz.questions.all())
        score = sum(
            1 for q in questions
            if QuizChoice.objects.filter(id=answer_map.get(q.id), question=q, is_correct=True).exists()
        )
        total = len(questions)

        submission = QuizSubmission.objects.create(
            student=request.user,
            quiz=quiz,
            selected_answers={str(k): v for k, v in answer_map.items()},
            score=score,
            total_questions=total,
        )

        percentage = round(score / total * 100) if total else 0
        return Response(
            {
                "status": "submitted",
                "message": "Quiz submitted.",
                "score": score,
                "total_questions": total,
                "percentage": percentage,
                "passed": percentage == 100,
                "attempt": QuizAttemptSerializer(submission).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TaskDetailView(APIView):
    """Task with instructions + this student's attempt history."""
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task = get_object_or_404(
            Task.objects.select_related("lesson__module__course"),
            id=task_id,
        )
        error = require_student_enrolled(request.user, task.lesson)
        if error:
            return error
        return Response(TaskWithAttemptsSerializer(task, context={"request": request}).data)


class SubmitTaskByIdView(APIView):
    """Submit a new task attempt by task ID."""
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        task = get_object_or_404(
            Task.objects.select_related("lesson__module__course__teacher"),
            id=task_id,
        )
        error = require_student_enrolled(request.user, task.lesson)
        if error:
            return error

        latest = TaskSubmission.objects.filter(task=task, student=request.user).order_by("-submitted_at").first()
        if latest:
            if latest.status == TaskSubmission.Status.SUBMITTED:
                return Response(
                    {"status": "pending_review", "message": "Your previous answer is still awaiting review."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if latest.passed:
                return Response(
                    {"status": "already_passed", "message": "You have already passed this task."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        answer_text = request.data.get("answer_text", "").strip()
        if not answer_text:
            return Response(
                {"status": "invalid", "message": "Answer text is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission = TaskSubmission.objects.create(
            student=request.user,
            task=task,
            answer_text=answer_text,
            status=TaskSubmission.Status.SUBMITTED,
        )

        create_notification(
            recipient=task.lesson.module.course.teacher,
            title="Written task submitted",
            message=f"{request.user.username} submitted '{task.title}'.",
            notification_type=Notification.Type.TASK_SUBMITTED,
            metadata={"task_id": task.id, "submission_id": submission.id},
        )

        return Response(
            {
                "status": "submitted",
                "message": "Answer submitted. Awaiting teacher review.",
                "attempt": TaskAttemptSerializer(submission).data,
            },
            status=status.HTTP_201_CREATED,
        )


class MyActivitiesView(APIView):
    """All quizzes and tasks from enrolled courses with attempt summary."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrolled_ids = Enrollment.objects.filter(
            student=request.user
        ).values_list("course_id", flat=True)

        quizzes = (
            Quiz.objects.filter(lesson__module__course_id__in=enrolled_ids)
            .select_related("lesson__module__course")
            .order_by("lesson__module__course__title", "lesson__title")
        )

        tasks = (
            Task.objects.filter(lesson__module__course_id__in=enrolled_ids)
            .select_related("lesson__module__course")
            .order_by("lesson__module__course__title", "lesson__title")
        )

        quiz_list = []
        for quiz in quizzes:
            attempts = QuizSubmission.objects.filter(quiz=quiz, student=request.user)
            count = attempts.count()
            best = attempts.order_by("-score").first()
            best_pct = round(best.score / best.total_questions * 100) if best and best.total_questions else None
            passed = best_pct == 100
            quiz_list.append({
                "id": quiz.id,
                "title": quiz.title,
                "lesson_id": quiz.lesson_id,
                "lesson_title": quiz.lesson.title,
                "course_title": quiz.lesson.module.course.title,
                "attempt_count": count,
                "best_percentage": best_pct,
                "passed": passed,
                "can_retry": not passed,
            })

        task_list = []
        for task in tasks:
            latest = TaskSubmission.objects.filter(task=task, student=request.user).order_by("-submitted_at").first()
            count = TaskSubmission.objects.filter(task=task, student=request.user).count()
            if latest is None:
                can_retry = True
            elif latest.status == TaskSubmission.Status.SUBMITTED:
                can_retry = False
            else:
                can_retry = not latest.passed
            task_list.append({
                "id": task.id,
                "title": task.title,
                "lesson_id": task.lesson_id,
                "lesson_title": task.lesson.title,
                "course_title": task.lesson.module.course.title,
                "attempt_count": count,
                "latest_status": latest.status if latest else None,
                "latest_score": latest.score if latest else None,
                "latest_passed": latest.passed if latest else None,
                "can_retry": can_retry,
            })

        return Response({"quizzes": quiz_list, "tasks": task_list})
