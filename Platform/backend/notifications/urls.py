from django.urls import path

from .views import MarkAllReadView, NotificationDetailView, NotificationListView, UnreadCountView

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', UnreadCountView.as_view(), name='notification-unread-count'),
    path('mark_all_read/', MarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('<int:pk>/mark_read/', NotificationDetailView.as_view(), name='notification-mark-read'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
]
