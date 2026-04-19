from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


def create_notification(recipient, notif_type, title, message, link='', extra=None):
    Notification.objects.create(
        recipient=recipient,
        type=notif_type,
        title=title,
        message=message,
        link=link,
        extra_data=extra or {},
    )


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(recipient=request.user)
        is_read_param = request.query_params.get('is_read')
        if is_read_param is not None:
            qs = qs.filter(is_read=is_read_param.lower() == 'true')
        paginator = NotificationPagination()
        page = paginator.paginate_queryset(qs, request)
        return paginator.get_paginated_response(NotificationSerializer(page, many=True).data)


class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, recipient=request.user)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)

    def delete(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, recipient=request.user)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'marked_read': count})


class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})
