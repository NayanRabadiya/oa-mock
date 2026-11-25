"""The acceptance tests for the watchlist feature. Run them with:  python manage.py test"""
from .base import M, WatchlistTestCase
from watchlist.models import Watchlist


class WatchlistTests(WatchlistTestCase):
    def test_get_watchlist_returns_movies_in_order_added(self):
        sam = self.client_for(self.sam)
        Watchlist.objects.create(user=self.sam, movie_id=M(3))
        Watchlist.objects.create(user=self.sam, movie_id=M(1))
        Watchlist.objects.create(user=self.alex, movie_id=M(2))
        response = sam.get("/api/watchlist/")
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertEqual([m["title"] for m in body], ["The Dark Knight", "The Shawshank Redemption"])
        self.assertEqual(set(body[0]), {"id", "title", "year", "genre"}, "each item is a movie document")

    def test_add_movie_creates_entry_and_rejects_duplicates(self):
        sam = self.client_for(self.sam)
        first = self.add(sam, M(2))
        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(first.json(), {"message": "Movie added to watchlist successfully"})
        self.assertTrue(Watchlist.objects.filter(user=self.sam, movie_id=M(2)).exists(), "the entry must be saved")
        again = self.add(sam, M(2))
        self.assertEqual(again.status_code, 400, again.content)
        self.assertEqual(again.json(), {"message": "Movie already in watchlist"})
        self.assertEqual(Watchlist.objects.filter(user=self.sam).count(), 1)

    def test_remove_movie_deletes_entry_and_404_when_missing(self):
        sam = self.client_for(self.sam)
        Watchlist.objects.create(user=self.sam, movie_id=M(4))
        removed = self.remove(sam, M(4))
        self.assertEqual(removed.status_code, 200, removed.content)
        self.assertEqual(removed.json(), {"message": "Movie removed from watchlist successfully"})
        self.assertFalse(Watchlist.objects.filter(user=self.sam, movie_id=M(4)).exists(), "the entry must be deleted")
        missing = self.remove(sam, M(4))
        self.assertEqual(missing.status_code, 404, missing.content)
        self.assertEqual(missing.json(), {"message": "Movie not found in watchlist"})

    def test_check_status_returns_boolean(self):
        sam = self.client_for(self.sam)
        before = sam.get("/api/watchlist/check/" + M(5))
        self.assertEqual(before.status_code, 200, before.content)
        self.assertIs(before.json()["isInWatchlist"], False)
        Watchlist.objects.create(user=self.sam, movie_id=M(5))
        after = sam.get("/api/watchlist/check/" + M(5))
        self.assertIs(after.json()["isInWatchlist"], True)

    def test_rate_limit_blocks_eleventh_operation_combined(self):
        sam = self.client_for(self.sam)
        for i in range(5):
            self.at(i * 2)
            self.assertEqual(self.add(sam, M(i + 1)).status_code, 201)
            self.at(i * 2 + 1)
            self.assertEqual(self.remove(sam, M(i + 1)).status_code, 200)
        self.at(11)
        blocked = self.add(sam, M(6))
        self.assertEqual(blocked.status_code, 429, "adds and removes share one limit of 10 per 2 minutes")
        self.assertEqual(blocked.json(), {"message": "Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes."})
        self.assertEqual(self.add(self.client_for(self.alex), M(6)).status_code, 201, "the limit is per user")

    def test_rate_limit_window_slides_after_two_minutes(self):
        sam = self.client_for(self.sam)
        for i in range(10):
            self.at(i)
            self.add(sam, M(1)) if i % 2 == 0 else self.remove(sam, M(1))
        self.at(60)
        self.assertEqual(self.add(sam, M(2)).status_code, 429)
        self.at(120)
        self.assertEqual(self.add(sam, M(2)).status_code, 201, "the request made at 0 s stops counting at 120 s")
        self.assertEqual(self.add(sam, M(3)).status_code, 429, "at 120 s the window holds 10 again (1 s ... 9 s and 120 s)")
        self.at(121)
        self.assertEqual(self.add(sam, M(3)).status_code, 201)
