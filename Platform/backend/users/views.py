from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer


def auth_response(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "user": UserProfileSerializer(profile).data,
    }


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(auth_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(auth_response(serializer.validated_data["user"]))


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        return Response(UserProfileSerializer(profile).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(
            {
                "message": "Logged out successfully.",
            }
        )


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
