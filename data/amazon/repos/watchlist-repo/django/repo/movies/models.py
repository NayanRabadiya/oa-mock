from django.conf import settings
from django.db import models


class Movie(models.Model):
    # Ids look like MongoDB ObjectIds (24 hex characters), as in the rest of the MovieDB platform.
    id = models.CharField(max_length=24, primary_key=True)
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    genre = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["movie", "user"], name="one_rating_per_user")]
