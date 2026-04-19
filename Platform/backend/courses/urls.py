from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CourseViewSet,
    LessonViewSet,
    ModuleViewSet,
    TeacherCourseCreateView,
    TeacherCourseDetailView,
    TeacherLessonCreateView,
    TeacherLessonDetailView,
    TeacherModuleCreateView,
    TeacherModuleDetailView,
    TeacherMyCoursesView,
    TeacherMyLessonsView,
    TeacherMyModulesView,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("courses", CourseViewSet, basename="course")
router.register("modules", ModuleViewSet, basename="module")
router.register("lessons", LessonViewSet, basename="lesson")

urlpatterns = [
    path("teacher/courses/", TeacherCourseCreateView.as_view(), name="teacher-create-course"),
    path("teacher/courses/<int:pk>/", TeacherCourseDetailView.as_view(), name="teacher-course-detail"),
    path("teacher/modules/", TeacherModuleCreateView.as_view(), name="teacher-create-module"),
    path("teacher/modules/<int:pk>/", TeacherModuleDetailView.as_view(), name="teacher-module-detail"),
    path("teacher/lessons/", TeacherLessonCreateView.as_view(), name="teacher-create-lesson"),
    path("teacher/lessons/<int:pk>/", TeacherLessonDetailView.as_view(), name="teacher-lesson-detail"),
    path("teacher/my-courses/", TeacherMyCoursesView.as_view(), name="teacher-my-courses"),
    path("teacher/my-modules/", TeacherMyModulesView.as_view(), name="teacher-my-modules"),
    path("teacher/my-lessons/", TeacherMyLessonsView.as_view(), name="teacher-my-lessons"),
    path("", include(router.urls)),
]
