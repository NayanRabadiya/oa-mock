"""The integrated tests for the library loans API. Run them with:  python manage.py test"""
from .base import LibraryTestCase


class LoanTests(LibraryTestCase):
    def test_borrowing_and_returning_a_book_changes_the_copies_on_the_shelf(self):
        self.assertEqual(self.available("B1"), 2)
        res = self.borrow("M1", "B1")
        self.assertEqual(res.status_code, 201, res.content)
        self.assertIncludes(res.json(), memberId="M1", bookId="B1", borrowedAt="2026-11-01", returnedAt=None)
        self.assertEqual(self.available("B1"), 1)
        self.assertEqual(self.give_back(res.json()["id"], "2026-11-10").status_code, 200)
        self.assertEqual(self.available("B1"), 2)

    def test_a_member_can_have_at_most_3_books_out(self):
        for book in ("B1", "B2", "B3"):
            self.assertEqual(self.borrow("M1", book).status_code, 201)
        fourth = self.borrow("M1", "B3")
        self.assertEqual((fourth.status_code, fourth.json()), (409, {"message": "Loan limit reached"}))
        self.assertEqual(self.borrow("M2", "B3").status_code, 201)

    def test_late_fees_start_after_the_14_day_loan_period(self):
        on_time = self.borrow("M1", "B1", "2026-11-01").json()
        self.assertIncludes(self.give_back(on_time["id"], "2026-11-15").json(), daysLate=0, fee=0)   # day 14: on time
        late = self.borrow("M1", "B1", "2026-11-01").json()
        self.assertIncludes(self.give_back(late["id"], "2026-11-18").json(), daysLate=3, fee=30)

    def test_a_loan_can_be_returned_only_once(self):
        loan = self.borrow("M1", "B1").json()
        self.assertEqual(self.give_back(loan["id"], "2026-11-05").status_code, 200)
        again = self.give_back(loan["id"], "2026-11-06")
        self.assertEqual((again.status_code, again.json()), (409, {"message": "Loan already returned"}))
