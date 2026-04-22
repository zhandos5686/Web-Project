from django.contrib import admin
from django.urls import include, path

from .views import api_root


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
