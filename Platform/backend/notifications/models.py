from django.db import models


class Notification(models.Model):
    class Type(models.TextChoices):
        BOOKING_CREATED = 'booking_created', 'New Booking'
        SUBMISSION_RECEIVED = 'submission_received', 'New Submission'
        TASK_GRADED = 'task_graded', 'Task Graded'
        LESSON_REMINDER = 'lesson_reminder', 'Lesson Reminder'
        SYSTEM = 'system', 'System'

    recipient = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE, related_name='notifications'
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient.username}: {self.title}'
