from django.conf import settings
from django.db import models

from movies.models import Movie


class Watchlist(models.Model):
    """One saved movie on one user's watchlist."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "movie"], name="unique_watchlist_entry")]

    def __str__(self):
        return "%s: %s" % (self.user, self.movie)
