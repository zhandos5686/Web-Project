from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CompleteLessonView,
    EnrollCourseView,
    EnrollmentViewSet,
    LessonQuizView,
    LessonTaskView,
    MyCoursesView,
    MyEnrollmentRequestsView,
    MyTaskSubmissionsView,
    ProgressRecordViewSet,
    ProgressSummaryView,
    SubmitQuizView,
    SubmitTaskView,
    TaskViewSet,
    TeacherQuizChoiceCreateView,
    TeacherQuizCreateView,
    TeacherQuizQuestionCreateView,
    TeacherQuizSubmissionsView,
    TeacherEnrollmentRequestsView,
    TeacherMyQuestionsView,
    TeacherMyQuizzesView,
    TeacherStudentProgressView,
    TeacherTaskCreateView,
    TeacherTaskSubmissionsView,
    TeacherUpdateEnrollmentRequestView,
)

router = DefaultRouter()
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
router.register("tasks", TaskViewSet, basename="task")
router.register("progress", ProgressRecordViewSet, basename="progress")

urlpatterns = [
    path("enroll/<int:course_id>/", EnrollCourseView.as_view(), name="enroll-course"),
    path("lessons/<int:lesson_id>/complete/", CompleteLessonView.as_view(), name="complete-lesson"),
    path("lessons/<int:lesson_id>/quiz/", LessonQuizView.as_view(), name="lesson-quiz"),
    path("lessons/<int:lesson_id>/quiz/submit/", SubmitQuizView.as_view(), name="submit-quiz"),
    path("lessons/<int:lesson_id>/task/", LessonTaskView.as_view(), name="lesson-task"),
    path("lessons/<int:lesson_id>/task/submit/", SubmitTaskView.as_view(), name="submit-task"),
    path("teacher/quizzes/", TeacherQuizCreateView.as_view(), name="teacher-create-quiz"),
    path("teacher/questions/", TeacherQuizQuestionCreateView.as_view(), name="teacher-create-question"),
    path("teacher/choices/", TeacherQuizChoiceCreateView.as_view(), name="teacher-create-choice"),
    path("teacher/tasks/", TeacherTaskCreateView.as_view(), name="teacher-create-task"),
    path("teacher/my-quizzes/", TeacherMyQuizzesView.as_view(), name="teacher-my-quizzes"),
    path("teacher/my-questions/", TeacherMyQuestionsView.as_view(), name="teacher-my-questions"),
    path("teacher/enrollment-requests/", TeacherEnrollmentRequestsView.as_view(), name="teacher-enrollment-requests"),
    path(
        "teacher/enrollment-requests/<int:request_id>/<str:action>/",
        TeacherUpdateEnrollmentRequestView.as_view(),
        name="teacher-update-enrollment-request",
    ),
    path("teacher/student-progress/", TeacherStudentProgressView.as_view(), name="teacher-student-progress"),
    path("teacher/quiz-submissions/", TeacherQuizSubmissionsView.as_view(), name="teacher-quiz-submissions"),
    path("teacher/task-submissions/", TeacherTaskSubmissionsView.as_view(), name="teacher-task-submissions"),
    path("my-courses/", MyCoursesView.as_view(), name="my-courses"),
    path("my-enrollment-requests/", MyEnrollmentRequestsView.as_view(), name="my-enrollment-requests"),
    path("my-task-submissions/", MyTaskSubmissionsView.as_view(), name="my-task-submissions"),
    path("progress-summary/", ProgressSummaryView.as_view(), name="progress-summary"),
    path("", include(router.urls)),
]
