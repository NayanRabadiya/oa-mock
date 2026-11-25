import secrets

from django.conf import settings
from django.db import models


class ApiToken(models.Model):
    """The bearer token a user gets when they log in."""

    key = models.CharField(max_length=64, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tokens")
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def issue(cls, user):
        return cls.objects.create(key=secrets.token_hex(24), user=user)
