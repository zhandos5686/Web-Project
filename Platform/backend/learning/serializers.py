from django.db import models
from rest_framework import serializers

from courses.serializers import CourseSerializer
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


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Enrollment
        fields = ["id", "student_username", "course", "created_at"]


class EnrollmentRequestSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = EnrollmentRequest
        fields = ["id", "student_username", "course", "status", "created_at", "updated_at"]


class TeacherStudentProgressSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    student_username = serializers.CharField()
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    completed_lessons = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    percentage = serializers.IntegerField()


class TaskSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(source="lesson.module.course.title", read_only=True)

    class Meta:
        model = Task
        fields = ["id", "lesson", "lesson_title", "course_title", "title", "instructions"]


class TeacherTaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "lesson", "title", "instructions"]

    def validate_lesson(self, value):
        request = self.context["request"]
        if value.module.course.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add written tasks only to lessons from their own courses.")
        if Task.objects.filter(lesson=value).exists():
            raise serializers.ValidationError("This lesson already has a written task.")
        return value


class TeacherTaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "title", "instructions"]


class TaskSubmissionSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    task_title = serializers.CharField(source="task.title", read_only=True)
    lesson_id = serializers.IntegerField(source="task.lesson.id", read_only=True)
    lesson_title = serializers.CharField(source="task.lesson.title", read_only=True)
    course_id = serializers.IntegerField(source="task.lesson.module.course.id", read_only=True)
    course_title = serializers.CharField(source="task.lesson.module.course.title", read_only=True)

    class Meta:
        model = TaskSubmission
        fields = [
            "id",
            "student_username",
            "task",
            "task_title",
            "lesson_id",
            "lesson_title",
            "course_id",
            "course_title",
            "answer_text",
            "status",
            "score",
            "teacher_feedback",
            "passed",
            "submitted_at",
            "updated_at",
            "reviewed_at",
        ]
        read_only_fields = ["id", "status", "score", "teacher_feedback", "passed", "submitted_at", "updated_at", "reviewed_at"]


class TeacherTaskSubmissionReviewSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=0, max_value=100)
    teacher_feedback = serializers.CharField(required=False, allow_blank=True)
    passed = serializers.BooleanField()


class QuizChoiceSerializer(serializers.ModelSerializer):
    question = serializers.IntegerField(source="question.id", read_only=True)
    question_text = serializers.CharField(source="question.text", read_only=True)
    quiz_title = serializers.CharField(source="question.quiz.title", read_only=True)
    lesson_title = serializers.CharField(source="question.quiz.lesson.title", read_only=True)
    course_title = serializers.CharField(source="question.quiz.lesson.module.course.title", read_only=True)

    class Meta:
        model = QuizChoice
        fields = [
            "id",
            "question",
            "question_text",
            "quiz_title",
            "lesson_title",
            "course_title",
            "text",
            "is_correct",
            "order",
        ]


class QuizQuestionSerializer(serializers.ModelSerializer):
    choices = QuizChoiceSerializer(many=True, read_only=True)
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    lesson_title = serializers.CharField(source="quiz.lesson.title", read_only=True)
    course_title = serializers.CharField(source="quiz.lesson.module.course.title", read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ["id", "quiz", "quiz_title", "lesson_title", "course_title", "text", "order", "choices"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(source="lesson.module.course.title", read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "lesson", "lesson_title", "course_title", "title", "questions"]


class TeacherQuizCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id", "lesson", "title"]

    def validate_lesson(self, value):
        request = self.context["request"]
        if value.module.course.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add quizzes only to lessons from their own courses.")
        if hasattr(value, "quiz"):
            raise serializers.ValidationError("This lesson already has a quiz.")
        return value


class TeacherQuizUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ["id", "title"]


class TeacherQuizQuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ["id", "quiz", "text", "order"]

    def validate_quiz(self, value):
        request = self.context["request"]
        if value.lesson.module.course.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add questions only to quizzes from their own courses.")
        return value


class TeacherQuizQuestionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ["id", "text", "order"]


class TeacherQuizChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ["id", "question", "text", "is_correct", "order"]

    def validate_question(self, value):
        request = self.context["request"]
        if value.quiz.lesson.module.course.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add choices only to questions from their own quizzes.")
        return value


class TeacherQuizChoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ["id", "text", "is_correct", "order"]


class QuizSubmissionSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    lesson_id = serializers.IntegerField(source="quiz.lesson.id", read_only=True)
    lesson_title = serializers.CharField(source="quiz.lesson.title", read_only=True)
    course_id = serializers.IntegerField(source="quiz.lesson.module.course.id", read_only=True)
    course_title = serializers.CharField(source="quiz.lesson.module.course.title", read_only=True)
    percentage = serializers.SerializerMethodField()

    def get_percentage(self, obj):
        if not obj.total_questions:
            return 0
        return round(obj.score / obj.total_questions * 100)

    class Meta:
        model = QuizSubmission
        fields = [
            "id",
            "student_username",
            "quiz",
            "quiz_title",
            "lesson_id",
            "lesson_title",
            "course_id",
            "course_title",
            "selected_answers",
            "score",
            "total_questions",
            "percentage",
            "submitted_at",
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Compact attempt record shown in student history."""
    percentage = serializers.SerializerMethodField()

    def get_percentage(self, obj):
        if not obj.total_questions:
            return 0
        return round(obj.score / obj.total_questions * 100)

    class Meta:
        model = QuizSubmission
        fields = ["id", "score", "total_questions", "percentage", "submitted_at"]


class QuizWithAttemptsSerializer(serializers.ModelSerializer):
    """Quiz detail + student's attempt history (requires request in context)."""
    questions = QuizQuestionSerializer(many=True, read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(source="lesson.module.course.title", read_only=True)
    lesson_id = serializers.IntegerField(source="lesson.id", read_only=True)
    attempts = serializers.SerializerMethodField()
    passed = serializers.SerializerMethodField()

    def get_attempts(self, obj):
        request = self.context.get("request")
        if not request:
            return []
        qs = QuizSubmission.objects.filter(quiz=obj, student=request.user).order_by("-submitted_at")
        return QuizAttemptSerializer(qs, many=True).data

    def get_passed(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        return QuizSubmission.objects.filter(
            quiz=obj, student=request.user, score=models.F("total_questions")
        ).exclude(total_questions=0).exists()

    class Meta:
        model = Quiz
        fields = ["id", "title", "lesson", "lesson_id", "lesson_title", "course_title", "questions", "attempts", "passed"]


class TaskAttemptSerializer(serializers.ModelSerializer):
    """Compact task attempt record shown in student history."""
    class Meta:
        model = TaskSubmission
        fields = ["id", "answer_text", "status", "score", "teacher_feedback", "passed", "submitted_at", "reviewed_at"]


class TaskWithAttemptsSerializer(serializers.ModelSerializer):
    """Task detail + student's attempt history (requires request in context)."""
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(source="lesson.module.course.title", read_only=True)
    lesson_id = serializers.IntegerField(source="lesson.id", read_only=True)
    attempts = serializers.SerializerMethodField()
    can_retry = serializers.SerializerMethodField()

    def get_attempts(self, obj):
        request = self.context.get("request")
        if not request:
            return []
        qs = TaskSubmission.objects.filter(task=obj, student=request.user).order_by("-submitted_at")
        return TaskAttemptSerializer(qs, many=True).data

    def get_can_retry(self, obj):
        request = self.context.get("request")
        if not request:
            return True
        latest = TaskSubmission.objects.filter(task=obj, student=request.user).order_by("-submitted_at").first()
        if latest is None:
            return True
        if latest.status == TaskSubmission.Status.SUBMITTED:
            return False  # Awaiting review
        return not latest.passed  # Can retry if not passed

    class Meta:
        model = Task
        fields = ["id", "title", "instructions", "lesson", "lesson_id", "lesson_title", "course_title", "attempts", "can_retry"]


class ProgressRecordSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = ProgressRecord
        fields = ["id", "student", "lesson", "lesson_title", "is_completed", "updated_at"]


class CourseProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    watched_percent = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    tasks_percent = serializers.IntegerField()
    overall_progress = serializers.IntegerField()
    percentage = serializers.IntegerField()  # kept for backward compatibility
