from django.conf import settings
from django.db import models


class LessonSlot(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    meeting_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.teacher.username}: {self.starts_at}"


class Booking(models.Model):
    slot = models.OneToOneField(LessonSlot, on_delete=models.CASCADE, related_name="booking")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} booked {self.slot}"
