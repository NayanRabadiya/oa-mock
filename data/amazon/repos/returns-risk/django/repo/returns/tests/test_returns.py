"""The integrated tests for the return/risk service. Run them with:  python manage.py test"""
from .base import ReturnsTestCase


class ReturnEvaluationTests(ReturnsTestCase):
    def test_accepts_a_return_on_the_last_day_of_the_window(self):
        self.order("O-1", "C5", delivered_at="2026-10-16")        # 30 days before 2026-11-15
        self.order("O-2", "C5", delivered_at="2026-10-15")        # 31 days before
        last_day = self.evaluate("O-1")
        self.assertEqual(last_day.status_code, 200, last_day.content)
        self.assertMatches(last_day, decision="AUTO_APPROVE", riskScore=0, reasons=[])
        self.assertMatches(self.evaluate("O-2"), decision="REJECT", reasons=["RETURN_WINDOW_EXPIRED"])

    def test_matches_categories_whatever_their_case(self):
        self.order("O-1", "C5", category="Electronics")
        self.order("O-2", "C5", category="HOME & KITCHEN")
        self.order("O-3", "C5", category="Grocery")
        self.assertEqual(self.evaluate("O-1").json()["decision"], "AUTO_APPROVE")
        self.assertEqual(self.evaluate("O-2").json()["decision"], "AUTO_APPROVE")
        self.assertMatches(self.evaluate("O-3"), decision="REJECT", reasons=["NON_RETURNABLE_CATEGORY"])

    def test_counts_returns_across_every_linked_account(self):
        self.past_return("C3", date="2026-10-01")                 # C3 is linked to C1 through C2
        self.past_return("C3", date="2026-11-02")
        self.order("O-1", "C1")
        self.assertMatches(self.evaluate("O-1"), decision="AUTO_APPROVE", riskScore=20, reasons=["RETURN_FREQUENCY"])

    def test_only_approved_returns_count_toward_the_history(self):
        self.past_return("C5", status="APPROVED")
        self.past_return("C5", status="REJECTED")
        self.past_return("C5", status="REJECTED")
        self.past_return("C5", status="PENDING_REVIEW")
        self.order("O-1", "C5")
        self.assertMatches(self.evaluate("O-1"), riskScore=10, reasons=["RETURN_FREQUENCY"])

    def test_scores_the_value_of_the_return_as_price_times_quantity(self):
        self.order("O-1", "C5", price=120, quantity=2)            # 240
        self.order("O-2", "C3", price=30, quantity=2)             # 60 (another customer: an approval goes into the history)
        self.assertMatches(self.evaluate("O-1"), riskScore=15, reasons=["ORDER_VALUE_ELEVATED"])
        self.assertMatches(self.evaluate("O-2"), riskScore=5, reasons=["ORDER_VALUE_MODERATE"])

    def test_decides_at_the_score_thresholds(self):
        self.past_return("C1", amount=1200)                       # +10 history, +15 refunded over 1000
        self.order("O-1", "C1", price=600)                        # +25 value, +20 changed mind = 70
        reject = self.evaluate("O-1", "CHANGED_MIND")
        self.assertMatches(reject, decision="REJECT", riskScore=70,
                           reasons=["REASON_DISCRETIONARY", "ORDER_VALUE_HIGH", "RETURN_FREQUENCY", "REFUND_TOTAL_HIGH", "HIGH_RISK"])

        self.past_return("C5", amount=20)                         # +10 history
        self.order("O-2", "C5")                                   # +20 changed mind = 30
        self.assertMatches(self.evaluate("O-2", "CHANGED_MIND"), decision="MANUAL_REVIEW", riskScore=30)

        self.order("O-3", "C9", price=300)                        # new account +10, +15 value = 25
        self.assertMatches(self.evaluate("O-3"), decision="AUTO_APPROVE", riskScore=25)
