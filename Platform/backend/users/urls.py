from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CurrentUserView, LoginView, LogoutView, RegisterView, UserProfileViewSet

router = DefaultRouter()
router.register("profiles", UserProfileViewSet, basename="profile")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-current-user"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("", include(router.urls)),
]
