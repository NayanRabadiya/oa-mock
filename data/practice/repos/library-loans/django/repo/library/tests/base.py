"""Shared setup for the library tests: a fresh store with three books and two members."""
import json

from django.test import SimpleTestCase

from library import store


class LibraryTestCase(SimpleTestCase):
    def setUp(self):
        store.reset({
            "books": [
                {"id": "B1", "title": "The Pragmatic Programmer", "copies": 2},
                {"id": "B2", "title": "Clean Code", "copies": 1},
                {"id": "B3", "title": "Refactoring", "copies": 5},
            ],
            "members": [{"id": "M1", "name": "Asha"}, {"id": "M2", "name": "Bilal"}],
            "loans": [],
        })

    def post(self, url, body):
        return self.client.post(url, data=json.dumps(body), content_type="application/json")

    def borrow(self, member_id, book_id, borrowed_at="2026-11-01"):
        return self.post("/api/loans", {"memberId": member_id, "bookId": book_id, "borrowedAt": borrowed_at})

    def give_back(self, loan_id, returned_at):
        return self.post("/api/loans/%s/return" % loan_id, {"returnedAt": returned_at})

    def available(self, book_id):
        return next(b["available"] for b in self.client.get("/api/books").json() if b["id"] == book_id)

    def assertIncludes(self, body, **expected):
        self.assertEqual({k: body.get(k) for k in expected}, expected, body)
