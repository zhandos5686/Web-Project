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
    class Meta:
        model = Task
        fields = ["id", "lesson", "title", "instructions"]


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
            "submitted_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "score", "submitted_at", "updated_at"]


class QuizChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ["id", "text", "order"]


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


class TeacherQuizQuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ["id", "quiz", "text", "order"]

    def validate_quiz(self, value):
        request = self.context["request"]
        if value.lesson.module.course.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add questions only to quizzes from their own courses.")
        return value


class TeacherQuizChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizChoice
        fields = ["id", "question", "text", "is_correct", "order"]

    def validate_question(self, value):
        request = self.context["request"]
        if value.quiz.lesson.module.course.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add choices only to questions from their own quizzes.")
        return value


class QuizSubmissionSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    lesson_id = serializers.IntegerField(source="quiz.lesson.id", read_only=True)
    lesson_title = serializers.CharField(source="quiz.lesson.title", read_only=True)
    course_id = serializers.IntegerField(source="quiz.lesson.module.course.id", read_only=True)
    course_title = serializers.CharField(source="quiz.lesson.module.course.title", read_only=True)

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
            "submitted_at",
        ]


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
    percentage = serializers.IntegerField()
