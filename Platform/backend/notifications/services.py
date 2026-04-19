from .models import Notification


def create_notification(recipient, title, message, notification_type, metadata=None):
    if recipient is None:
        return None

    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        type=notification_type,
        metadata=metadata or {},
    )
