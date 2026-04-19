from django.urls import path

from .views import (
    DeleteNotificationView,
    MarkAllNotificationsReadView,
    MarkNotificationReadView,
    NotificationListView,
    UnreadNotificationCountView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("unread-count/", UnreadNotificationCountView.as_view(), name="notification-unread-count"),
    path("<int:notification_id>/mark-read/", MarkNotificationReadView.as_view(), name="notification-mark-read"),
    path("mark-all-read/", MarkAllNotificationsReadView.as_view(), name="notification-mark-all-read"),
    path("<int:notification_id>/", DeleteNotificationView.as_view(), name="notification-delete"),
]
