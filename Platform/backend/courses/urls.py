from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CourseViewSet,
    LessonViewSet,
    ModuleViewSet,
    TeacherCourseCreateView,
    TeacherLessonCreateView,
    TeacherModuleCreateView,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("courses", CourseViewSet, basename="course")
router.register("modules", ModuleViewSet, basename="module")
router.register("lessons", LessonViewSet, basename="lesson")

urlpatterns = [
    path("teacher/courses/", TeacherCourseCreateView.as_view(), name="teacher-create-course"),
    path("teacher/modules/", TeacherModuleCreateView.as_view(), name="teacher-create-module"),
    path("teacher/lessons/", TeacherLessonCreateView.as_view(), name="teacher-create-lesson"),
    path("", include(router.urls)),
]
