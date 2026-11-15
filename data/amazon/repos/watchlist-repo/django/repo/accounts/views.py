from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .models import ApiToken


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def login(request):
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""
    user = get_user_model().objects.filter(email=email).first()
    if user is None or authenticate(username=user.username, password=password) is None:
        return Response({"message": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
    token = ApiToken.issue(user)
    return Response({"token": token.key, "user": {"id": user.pk, "name": user.first_name, "email": user.email}})
