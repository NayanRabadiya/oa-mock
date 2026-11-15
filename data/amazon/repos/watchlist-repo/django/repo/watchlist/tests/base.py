"""Shared setup for the watchlist tests: a fresh database with the sample movies and two users."""
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import ApiToken
from movies.models import Movie

M = lambda i: "65f0a1b2c3d4e5f6%08d" % i
TITLES = ["The Shawshank Redemption", "Interstellar", "The Dark Knight", "Spirited Away", "Parasite", "Inception"]


class WatchlistTestCase(TestCase):
    def setUp(self):
        cache.clear()
        for i, title in enumerate(TITLES, 1):
            Movie.objects.create(id=M(i), title=title, year=2000 + i, genre="Drama")
        User = get_user_model()
        self.sam = User.objects.create_user("sam", "sam.rivera@email.com", "Password@123")
        self.alex = User.objects.create_user("alex", "alex.chen@email.com", "Password@123")
        self.clock = 1_700_000_000.0
        patcher = mock.patch("watchlist.throttling.now", side_effect=lambda: self.clock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def client_for(self, user):
        client = APIClient()
        if user is not None:
            client.credentials(HTTP_AUTHORIZATION="Bearer " + ApiToken.issue(user).key)
        return client

    def at(self, seconds):
        """Moves the clock the rate limiter sees to `seconds` after the start of the test."""
        self.clock = 1_700_000_000.0 + seconds

    def add(self, client, movie_id):
        return client.post("/api/watchlist/add", {"movieId": movie_id}, format="json")

    def remove(self, client, movie_id):
        return client.post("/api/watchlist/remove", {"movieId": movie_id}, format="json")

    def titles(self, client):
        response = client.get("/api/watchlist/")
        self.assertEqual(response.status_code, 200, response.content)
        return [movie["title"] for movie in response.json()]
