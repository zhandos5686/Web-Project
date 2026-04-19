from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'link', 'is_read', 'created_at', 'extra_data']
        read_only_fields = ['id', 'type', 'title', 'message', 'link', 'created_at', 'extra_data']
