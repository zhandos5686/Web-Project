from django.urls import path
from .views import (
    category_list,
    category_detail,
    course_list,
    course_detail,
    TaskListAPIView,
    TaskDetailAPIView,
    EnrollmentListAPIView,
    EnrollmentDetailAPIView,
    ProfileAPIView,
    MyCoursesAPIView,
    MyTasksAPIView,
    enroll_in_course,
    complete_task,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('categories/', category_list),
    path('categories/<int:category_id>/', category_detail),

    path('courses/', course_list),
    path('courses/<int:course_id>/', course_detail),

    path('tasks/', TaskListAPIView.as_view()),
    path('tasks/<int:task_id>/', TaskDetailAPIView.as_view()),

    path('enrollments/', EnrollmentListAPIView.as_view()),
    path('enrollments/<int:enrollment_id>/', EnrollmentDetailAPIView.as_view()),

    path('profile/', ProfileAPIView.as_view()),
    path('my-courses/', MyCoursesAPIView.as_view()),
    path('my-tasks/', MyTasksAPIView.as_view()),
    path('enroll/', enroll_in_course),
    path('tasks/<int:task_id>/complete/', complete_task),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]