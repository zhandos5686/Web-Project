from rest_framework import serializers

from .models import Category, Course, Lesson, Module


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class LessonSerializer(serializers.ModelSerializer):
    module_title = serializers.CharField(source="module.title", read_only=True)
    course_id = serializers.IntegerField(source="module.course.id", read_only=True)
    course_title = serializers.CharField(source="module.course.title", read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "youtube_url",
            "content",
            "order",
            "module_title",
            "course_id",
            "course_title",
        ]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Module
        fields = ["id", "course_id", "course_title", "title", "order", "lessons"]


class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source="teacher.username", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "level",
            "image_url",
            "category",
            "teacher_name",
            "is_published",
            "modules",
        ]


class TeacherCourseCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    category_name = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "level",
            "image_url",
            "category_id",
            "category_name",
            "is_published",
        ]

    def validate_category_id(self, value):
        if value is not None and not Category.objects.filter(id=value).exists():
            raise serializers.ValidationError("Category not found.")
        return value

    def create(self, validated_data):
        category_id = validated_data.pop("category_id", None)
        category_name = validated_data.pop("category_name", "").strip()
        category = None

        if category_id:
            category = Category.objects.get(id=category_id)
        elif category_name:
            category, _ = Category.objects.get_or_create(name=category_name)

        return Course.objects.create(
            category=category,
            teacher=self.context["request"].user,
            **validated_data,
        )


class TeacherModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ["id", "course", "title", "order"]

    def validate_course(self, value):
        request = self.context["request"]
        if value.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add modules only to their own courses.")
        return value


class TeacherLessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "module", "title", "youtube_url", "content", "order"]

    def validate_module(self, value):
        request = self.context["request"]
        if value.course.teacher_id != request.user.id:
            raise serializers.ValidationError("Ownership error: teachers can add lessons only to modules from their own courses.")
        return value
