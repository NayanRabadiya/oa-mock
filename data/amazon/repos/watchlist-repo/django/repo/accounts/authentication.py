"""authMiddleware: reads `Authorization: Bearer <token>` and sets request.user (401 otherwise)."""
from rest_framework import authentication, exceptions

from .models import ApiToken


class BearerTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header:
            return None
        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            raise exceptions.AuthenticationFailed("Unauthorized")
        try:
            token = ApiToken.objects.select_related("user").get(key=parts[1])
        except ApiToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Unauthorized")
        return token.user, token

    def authenticate_header(self, request):
        return self.keyword
