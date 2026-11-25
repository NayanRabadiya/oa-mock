"""Every error response has the same shape as the rest of the API: {"message": "..."}."""
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler

RATE_LIMIT_MESSAGE = "Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes."


def api_exception_handler(exc, context):
    if isinstance(exc, exceptions.Throttled):
        return Response({"message": RATE_LIMIT_MESSAGE}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    response = exception_handler(exc, context)
    if response is not None and isinstance(response.data, dict) and "detail" in response.data:
        response.data = {"message": str(response.data["detail"])}
    return response
