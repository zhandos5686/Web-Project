import json
import urllib.parse
import urllib.request

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

MAX_LENGTH = 50


@api_view(["POST"])
@permission_classes([AllowAny])
def translate_text(request):
    text = request.data.get("text", "").strip()

    if not text:
        return Response({"error": "Текст не указан."}, status=status.HTTP_400_BAD_REQUEST)

    if len(text) > MAX_LENGTH:
        return Response({"error": "Текст слишком длинный."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        params = urllib.parse.urlencode({"q": text, "langpair": "en|ru"})
        url = f"https://api.mymemory.translated.net/get?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8"))

        translated = data.get("responseData", {}).get("translatedText", "").strip()

        if not translated or translated.lower() == text.lower():
            return Response({"error": "Перевод недоступен."})

        return Response({"translated": translated})

    except Exception:
        return Response(
            {"error": "Сервис перевода недоступен."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
