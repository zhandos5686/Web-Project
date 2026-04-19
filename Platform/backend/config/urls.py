from django.contrib import admin
from django.urls import include, path
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def api_root(request):
    return Response(
        {
            "message": "English Learning Platform API",
            "version": "v1",
            "endpoints": {
                "users": "/api/users/",
                "courses": "/api/courses/",
                "learning": "/api/learning/",
                "booking": "/api/booking/",
                "notifications": "/api/notifications/",
            },
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),
    path("api/users/", include("users.urls")),
    path("api/courses/", include("courses.urls")),
    path("api/learning/", include("learning.urls")),
    path("api/booking/", include("booking.urls")),
    path("api/notifications/", include("notifications.urls")),
    path("api/translate/", include("translate.urls")),
]
