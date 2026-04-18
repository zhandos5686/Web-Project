from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course, Lesson
from users.models import UserProfile
from users.permissions import IsTeacher
from .models import Enrollment, EnrollmentRequest, ProgressRecord, Quiz, QuizChoice, QuizSubmission, Task, TaskSubmission
from .serializers import (
    CourseProgressSerializer,
    EnrollmentRequestSerializer,
    EnrollmentSerializer,
    ProgressRecordSerializer,
    QuizSerializer,
    QuizSubmissionSerializer,
    TaskSerializer,
    TaskSubmissionSerializer,
    TeacherQuizChoiceCreateSerializer,
    TeacherQuizCreateSerializer,
    TeacherQuizQuestionCreateSerializer,
    TeacherStudentProgressSerializer,
    TeacherTaskCreateSerializer,
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
            .select_related("student", "course", "course__category", "course__teacher")
            .prefetch_related("course__modules__lessons")
            .order_by("status", "-updated_at")
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


class ProgressSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = (
            Enrollment.objects.filter(student=request.user)
            .select_related("course")
            .prefetch_related("course__modules__lessons")
            .order_by("-created_at")
        )

        progress_items = []
        for enrollment in enrollments:
            course = enrollment.course
            lesson_ids = [
                lesson.id
                for module in course.modules.all()
                for lesson in module.lessons.all()
            ]
            total_lessons = len(lesson_ids)
            completed_lessons = ProgressRecord.objects.filter(
                student=request.user,
                lesson_id__in=lesson_ids,
                is_completed=True,
            ).count()
            percentage = round((completed_lessons / total_lessons) * 100) if total_lessons else 0

            progress_items.append(
                {
                    "course_id": course.id,
                    "course_title": course.title,
                    "total_lessons": total_lessons,
                    "completed_lessons": completed_lessons,
                    "percentage": percentage,
                }
            )

        serializer = CourseProgressSerializer(progress_items, many=True)
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

        questions = list(quiz.questions.prefetch_related("choices"))
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
        lesson = get_object_or_404(Lesson.objects.select_related("module", "module__course"), id=lesson_id)
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

        submission, created = TaskSubmission.objects.update_or_create(
            student=request.user,
            task=task,
            defaults={
                "answer_text": answer_text,
                "status": TaskSubmission.Status.SUBMITTED,
                "score": None,
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


class ProgressRecordViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgressRecordSerializer

    def get_queryset(self):
        return ProgressRecord.objects.filter(student=self.request.user).select_related("student", "lesson")
