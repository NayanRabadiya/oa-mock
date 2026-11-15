"""More acceptance tests (hidden in the test: they run when you submit)."""
from .base import M, WatchlistTestCase
from watchlist.models import Watchlist


class MoreWatchlistTests(WatchlistTestCase):
    def test_add_validation_errors(self):
        sam = self.client_for(self.sam)
        for body, code, message in (({}, 400, "Movie ID is required"), ({"movieId": "123"}, 400, "Invalid movie ID format"),
                                    ({"movieId": M(999)}, 404, "Movie not found")):
            response = sam.post("/api/watchlist/add", body, format="json")
            self.assertEqual((response.status_code, response.json()), (code, {"message": message}))
        self.assertEqual(Watchlist.objects.count(), 0)

    def test_remove_and_check_validation_errors(self):
        sam = self.client_for(self.sam)
        self.assertEqual(sam.post("/api/watchlist/remove", {}, format="json").json(), {"message": "Movie ID is required"})
        bad = self.remove(sam, "not-an-id")
        self.assertEqual((bad.status_code, bad.json()), (400, {"message": "Invalid movie ID format"}))
        check = sam.get("/api/watchlist/check/xyz")
        self.assertEqual((check.status_code, check.json()), (400, {"message": "Invalid movie ID format"}))

    def test_every_route_needs_a_token(self):
        anonymous = self.client_for(None)
        for response in (anonymous.get("/api/watchlist/"), anonymous.get("/api/watchlist/check/" + M(1)),
                         self.add(anonymous, M(1)), self.remove(anonymous, M(1))):
            self.assertEqual((response.status_code, response.json()), (401, {"message": "Unauthorized"}))

    def test_watchlists_are_per_user(self):
        sam, alex = self.client_for(self.sam), self.client_for(self.alex)
        self.add(sam, M(1)); self.add(sam, M(3)); self.add(alex, M(4))
        self.assertEqual(self.titles(sam), ["The Shawshank Redemption", "The Dark Knight"])
        self.assertEqual(self.titles(alex), ["Spirited Away"])
        self.assertEqual(self.remove(alex, M(1)).status_code, 404, "alex can't remove sam's movie")
        self.assertIs(alex.get("/api/watchlist/check/" + M(1)).json()["isInWatchlist"], False)

    def test_add_remove_and_add_again(self):
        sam = self.client_for(self.sam)
        self.assertEqual(self.add(sam, M(5)).status_code, 201)
        self.assertEqual(self.remove(sam, M(5)).status_code, 200)
        self.assertEqual(self.titles(sam), [])
        self.assertEqual(self.add(sam, M(5)).status_code, 201)
        self.assertEqual(self.add(sam, M(2)).status_code, 201)
        self.assertEqual(self.titles(sam), ["Parasite", "Interstellar"])

    def test_failed_requests_count_toward_the_limit(self):
        sam = self.client_for(self.sam)
        for i in range(10):
            self.at(i)
            self.assertEqual(self.add(sam, "bad%d" % i).status_code, 400)
        self.at(10)
        self.assertEqual(self.add(sam, M(2)).status_code, 429)
        self.assertEqual(self.titles(sam), [])

    def test_rejected_requests_do_not_count(self):
        sam = self.client_for(self.sam)
        for i in range(10):
            self.at(i)
            self.add(sam, M(1)) if i % 2 == 0 else self.remove(sam, M(1))
        for t in (30, 60, 90, 119):
            self.at(t)
            self.assertEqual(self.add(sam, M(2)).status_code, 429)
        self.at(120)
        self.assertEqual(self.add(sam, M(2)).status_code, 201, "429 responses must not extend the window")

    def test_reads_are_not_rate_limited(self):
        sam = self.client_for(self.sam)
        for i in range(10):
            self.at(i)
            self.add(sam, M(1)) if i % 2 == 0 else self.remove(sam, M(1))
        self.at(11)
        for _ in range(15):
            self.assertEqual(sam.get("/api/watchlist/").status_code, 200)
            self.assertEqual(sam.get("/api/watchlist/check/" + M(1)).status_code, 200)
