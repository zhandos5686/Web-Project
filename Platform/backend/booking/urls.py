from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvailableSlotsView,
    BookingViewSet,
    BookSlotView,
    LessonSlotViewSet,
    StudentMyBookingsView,
    TeacherCreateSlotView,
    TeacherDeleteSlotView,
    TeacherMySlotsView,
    TeacherSlotBookingsView,
)

router = DefaultRouter()
router.register("slots", LessonSlotViewSet, basename="slot")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = [
    path("teacher/slots/", TeacherCreateSlotView.as_view(), name="teacher-create-slot"),
    path("teacher/slots/<int:slot_id>/", TeacherDeleteSlotView.as_view(), name="teacher-delete-slot"),
    path("teacher/my-slots/", TeacherMySlotsView.as_view(), name="teacher-my-slots"),
    path("teacher/bookings/", TeacherSlotBookingsView.as_view(), name="teacher-slot-bookings"),
    path("available-slots/", AvailableSlotsView.as_view(), name="available-slots"),
    path("book/<int:slot_id>/", BookSlotView.as_view(), name="book-slot"),
    path("my-bookings/", StudentMyBookingsView.as_view(), name="student-my-bookings"),
    path("", include(router.urls)),
]
