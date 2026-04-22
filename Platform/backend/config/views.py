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
                "translate": "/api/translate/",
            },
        }
    )
