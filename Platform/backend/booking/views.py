from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Booking, LessonSlot
from .serializers import BookingSerializer, LessonSlotSerializer
from notifications.models import Notification
from notifications.services import create_notification
from users.models import UserProfile
from users.permissions import IsTeacher


def is_student(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.role == UserProfile.Role.STUDENT


class LessonSlotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LessonSlot.objects.select_related("teacher").order_by("starts_at")
    serializer_class = LessonSlotSerializer


class BookingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Booking.objects.select_related("slot", "slot__teacher", "student")
    serializer_class = BookingSerializer


class TeacherCreateSlotView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def post(self, request):
        serializer = LessonSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        slot = serializer.save(teacher=request.user, is_available=True)
        return Response(
            {
                "status": "slot_created",
                "message": "Live lesson slot created successfully.",
                "slot": LessonSlotSerializer(slot).data,
            },
            status=status.HTTP_201_CREATED,
        )


class TeacherMySlotsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        slots = (
            LessonSlot.objects.filter(teacher=request.user)
            .select_related("teacher", "booking", "booking__student")
            .order_by("starts_at")
        )
        return Response(LessonSlotSerializer(slots, many=True).data)


class TeacherDeleteSlotView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def delete(self, request, slot_id):
        slot = get_object_or_404(LessonSlot, id=slot_id, teacher=request.user)
        if hasattr(slot, "booking"):
            return Response(
                {
                    "status": "cannot_delete_booked_slot",
                    "message": "This slot already has a booking and cannot be deleted in V1.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        slot.delete()
        return Response(
            {
                "status": "slot_deleted",
                "message": "Live lesson slot deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class TeacherSlotBookingsView(APIView):
    permission_classes = [IsAuthenticated, IsTeacher]

    def get(self, request):
        bookings = (
            Booking.objects.filter(slot__teacher=request.user)
            .select_related("slot", "slot__teacher", "student")
            .order_by("slot__starts_at")
        )
        return Response(BookingSerializer(bookings, many=True).data)


class AvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_student(request.user):
            return Response(
                {
                    "status": "forbidden",
                    "message": "Only student users can view available slots for booking.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        slots = (
            LessonSlot.objects.filter(is_available=True, booking__isnull=True)
            .select_related("teacher")
            .order_by("starts_at")
        )
        return Response(LessonSlotSerializer(slots, many=True).data)


class BookSlotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, slot_id):
        if not is_student(request.user):
            return Response(
                {
                    "status": "forbidden",
                    "message": "Only student users can book live lesson slots.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        slot = get_object_or_404(LessonSlot.objects.select_related("teacher"), id=slot_id)
        if not slot.is_available or hasattr(slot, "booking"):
            return Response(
                {
                    "status": "already_booked",
                    "message": "This live lesson slot is already booked.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                booking = Booking.objects.create(slot=slot, student=request.user)
                slot.is_available = False
                slot.save(update_fields=["is_available"])
        except IntegrityError:
            booking = Booking.objects.select_related("slot", "slot__teacher", "student").get(slot=slot)
            return Response(
                {
                    "status": "already_booked",
                    "message": "This live lesson slot is already booked.",
                    "booking": BookingSerializer(booking).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_notification(
            recipient=slot.teacher,
            title="Live lesson slot booked",
            message=f"{request.user.username} booked your live lesson slot on {slot.starts_at:%Y-%m-%d %H:%M}.",
            notification_type=Notification.Type.BOOKING_CREATED,
            metadata={
                "slot_id": slot.id,
                "booking_id": booking.id,
                "student_username": request.user.username,
            },
        )

        return Response(
            {
                "status": "slot_booked",
                "message": "Live lesson slot booked successfully.",
                "booking": BookingSerializer(booking).data,
            },
            status=status.HTTP_201_CREATED,
        )


class StudentMyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not is_student(request.user):
            return Response(
                {
                    "status": "forbidden",
                    "message": "Only student users can view their booked lessons here.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        bookings = (
            Booking.objects.filter(student=request.user)
            .select_related("slot", "slot__teacher", "student")
            .order_by("slot__starts_at")
        )
        return Response(BookingSerializer(bookings, many=True).data)
