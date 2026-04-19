from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Category, Course, Lesson, Module
from users.permissions import IsTeacher
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    TeacherCourseCreateSerializer,
    TeacherCourseUpdateSerializer,
    TeacherLessonCreateSerializer,
    TeacherLessonUpdateSerializer,
    TeacherModuleCreateSerializer,
    TeacherModuleUpdateSerializer,
)


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        Course.objects.filter(is_published=True)
        .select_related("category", "teacher")
        .prefetch_related("modules__lessons")
        .order_by("id")
    )
    serializer_class = CourseSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.prefetch_related("courses").all()
    serializer_class = CategorySerializer


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Module.objects.select_related("course").prefetch_related("lessons")
    serializer_class = ModuleSerializer


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.select_related("module", "module__course").order_by("module__order", "order", "id")
    serializer_class = LessonSerializer


class TeacherCourseCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherCourseCreateSerializer


class TeacherModuleCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherModuleCreateSerializer


class TeacherLessonCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = TeacherLessonCreateSerializer


class TeacherOwnedContentMixin:
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


class TeacherCourseDetailView(TeacherOwnedContentMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.select_related("category", "teacher").prefetch_related("modules__lessons")
    serializer_class = TeacherCourseUpdateSerializer
    ownership_error_message = "You can edit or delete only your own courses."
    delete_success_message = "Course deleted successfully."
    http_method_names = ["patch", "delete", "options"]

    def check_owner(self, obj):
        return obj.teacher_id == self.request.user.id


class TeacherModuleDetailView(TeacherOwnedContentMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.select_related("course", "course__teacher").prefetch_related("lessons")
    serializer_class = TeacherModuleUpdateSerializer
    ownership_error_message = "You can edit or delete only modules from your own courses."
    delete_success_message = "Module deleted successfully."
    http_method_names = ["patch", "delete", "options"]

    def check_owner(self, obj):
        return obj.course.teacher_id == self.request.user.id


class TeacherLessonDetailView(TeacherOwnedContentMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.select_related("module", "module__course", "module__course__teacher")
    serializer_class = TeacherLessonUpdateSerializer
    ownership_error_message = "You can edit or delete only lessons from your own courses."
    delete_success_message = "Lesson deleted successfully."
    http_method_names = ["patch", "delete", "options"]

    def check_owner(self, obj):
        return obj.module.course.teacher_id == self.request.user.id


class TeacherMyCoursesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CourseSerializer

    def get_queryset(self):
        return (
            Course.objects.filter(teacher=self.request.user)
            .select_related("category", "teacher")
            .prefetch_related("modules__lessons")
            .order_by("id")
        )


class TeacherMyModulesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = ModuleSerializer

    def get_queryset(self):
        return (
            Module.objects.filter(course__teacher=self.request.user)
            .select_related("course", "course__teacher")
            .prefetch_related("lessons")
            .order_by("course__title", "order", "id")
        )


class TeacherMyLessonsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = LessonSerializer

    def get_queryset(self):
        return (
            Lesson.objects.filter(module__course__teacher=self.request.user)
            .select_related("module", "module__course", "module__course__teacher")
            .order_by("module__course__title", "module__order", "order", "id")
        )
