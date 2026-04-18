from rest_framework.permissions import BasePermission

from .models import UserProfile


class IsTeacher(BasePermission):
    message = "Only teacher users can use this endpoint."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return profile.role == UserProfile.Role.TEACHER
