from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Category, Course, Lesson, Module
from users.permissions import IsTeacher
from .serializers import (
    CategorySerializer,
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    TeacherCourseCreateSerializer,
    TeacherLessonCreateSerializer,
    TeacherModuleCreateSerializer,
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
