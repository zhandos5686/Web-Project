from rest_framework import serializers

from .models import Booking, LessonSlot


class SlotBookingSummarySerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "student_username", "created_at"]


class LessonSlotSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source="teacher.username", read_only=True)
    booking = SlotBookingSummarySerializer(read_only=True)

    class Meta:
        model = LessonSlot
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "starts_at",
            "ends_at",
            "meeting_url",
            "is_available",
            "booking",
        ]
        read_only_fields = ["id", "teacher", "teacher_name", "is_available"]

    def validate(self, attrs):
        starts_at = attrs.get("starts_at")
        ends_at = attrs.get("ends_at")
        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError("Slot end time must be after start time.")
        return attrs


class SlotBookingInfoSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)

    class Meta:
        model = Booking
        fields = ["student_username", "created_at"]


class TeacherLessonSlotSerializer(serializers.ModelSerializer):
    booking = SlotBookingInfoSerializer(read_only=True)

    class Meta:
        model = LessonSlot
        fields = ["id", "starts_at", "ends_at", "meeting_url", "is_available", "booking"]
        read_only_fields = ["id", "is_available"]

    def validate(self, attrs):
        starts_at = attrs.get("starts_at")
        ends_at = attrs.get("ends_at")
        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError("Slot end time must be after start time.")
        return attrs


class BookingSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source="student.username", read_only=True)
    slot = LessonSlotSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "slot", "student_username", "created_at"]
