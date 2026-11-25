"""More integrated tests (hidden in the test: they run when you submit)."""
from .base import LibraryTestCase


class MoreLoanTests(LibraryTestCase):
    def test_validates_the_request(self):
        self.assertEqual(self.post("/api/loans", {"memberId": "M1"}).json(), {"message": "memberId and bookId are required"})
        self.assertEqual(self.borrow("M9", "B1").status_code, 404)
        self.assertEqual(self.borrow("M1", "B9").json(), {"message": "Book not found"})
        self.assertEqual(self.borrow("M1", "B1", "1/11/2026").status_code, 400)
        self.assertEqual(self.give_back("L99", "2026-11-05").json(), {"message": "Loan not found"})

    def test_a_book_with_every_copy_out_cannot_be_borrowed(self):
        self.assertEqual(self.borrow("M1", "B2").status_code, 201)
        none = self.borrow("M2", "B2")
        self.assertEqual((none.status_code, none.json()), (409, {"message": "No copies available"}))

    def test_the_fee_for_one_loan_is_at_most_200(self):
        loan = self.borrow("M1", "B1", "2026-10-01").json()
        self.assertIncludes(self.give_back(loan["id"], "2026-11-15").json(), daysLate=31, fee=200)
