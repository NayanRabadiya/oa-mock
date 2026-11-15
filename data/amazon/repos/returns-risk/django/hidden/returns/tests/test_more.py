"""More integrated tests (hidden in the test: they run when you submit)."""
from .base import ReturnsTestCase


class MoreReturnEvaluationTests(ReturnsTestCase):
    def test_validates_the_request(self):
        self.order("O-1", "C5")
        missing = self.post({"orderId": "O-1"})
        self.assertEqual((missing.status_code, missing.json()), (400, {"message": "orderId, itemId and reason are required"}))
        self.assertEqual(self.evaluate("O-1", "BORED").json(), {"message": "Invalid return reason"})
        self.assertEqual(self.evaluate("O-1", requestedAt="15/11/2026").status_code, 400)
        no_order = self.evaluate("O-404")
        self.assertEqual((no_order.status_code, no_order.json()), (404, {"message": "Order not found"}))
        no_item = self.evaluate("O-1", itemId="I-9")
        self.assertEqual((no_item.status_code, no_item.json()), (404, {"message": "Item not found in order"}))

    def test_rejects_orders_that_have_not_been_delivered(self):
        self.order("O-1", "C5", status="SHIPPED", delivered_at=None)
        self.assertMatches(self.evaluate("O-1"), decision="REJECT", riskScore=0, reasons=["NOT_DELIVERED"])

    def test_an_item_can_have_only_one_open_return(self):
        self.order("O-1", "C5")
        self.assertEqual(self.evaluate("O-1").json()["decision"], "AUTO_APPROVE")
        self.assertMatches(self.evaluate("O-1"), decision="REJECT", reasons=["ALREADY_RETURNED"])
        self.order("O-2", "C5")
        self.past_return("C5", order_id="O-2", status="REJECTED")   # a rejected return doesn't block a new one
        self.assertNotIn("ALREADY_RETURNED", self.evaluate("O-2").json()["reasons"])

    def test_caps_the_score_at_100(self):
        for i in range(5):
            self.past_return("C9", amount=300, date="2026-11-0%d" % (i + 2))
        self.order("O-1", "C9", price=800)
        self.assertMatches(self.evaluate("O-1", "NO_LONGER_NEEDED"), decision="REJECT", riskScore=100,
                           reasons=["REASON_DISCRETIONARY", "ORDER_VALUE_HIGH", "RETURN_FREQUENCY", "REFUND_TOTAL_HIGH", "NEW_ACCOUNT", "HIGH_RISK"])

    def test_history_covers_the_90_days_before_the_request(self):
        self.past_return("C5", date="2026-08-17")                   # 90 days before: counts
        self.past_return("C5", date="2026-08-16")                   # 91 days before: doesn't
        self.past_return("C5", date="2026-11-20")                   # after the request: doesn't
        self.order("O-1", "C5")
        self.assertMatches(self.evaluate("O-1"), riskScore=10, reasons=["RETURN_FREQUENCY"])

    def test_the_refund_total_must_be_more_than_1000(self):
        self.past_return("C5", amount=500)
        self.past_return("C5", amount=500)
        self.order("O-1", "C5")
        self.assertEqual(self.evaluate("O-1").json()["reasons"], ["RETURN_FREQUENCY"])
        self.past_return("C5", amount=0.01)
        self.assertEqual(self.evaluate("O-1").json()["reasons"], ["RETURN_FREQUENCY", "REFUND_TOTAL_HIGH"])

    def test_every_reason_comes_with_its_message(self):
        self.order("O-1", "C9", price=75)
        res = self.evaluate("O-1", "NOT_AS_DESCRIBED")
        self.assertMatches(res, decision="AUTO_APPROVE", riskScore=25,
                           reasons=["REASON_NOT_AS_DESCRIBED", "ORDER_VALUE_MODERATE", "NEW_ACCOUNT"],
                           messages=["The customer says the item is not as described", "The return is worth 50 or more",
                                     "The account is less than 30 days old"])

    def test_evaluations_are_recorded_in_the_history(self):
        self.order("O-1", "C5", price=45, quantity=2)
        self.order("O-2", "C5")
        first = self.evaluate("O-1").json()
        self.assertEqual(first["decision"], "AUTO_APPROVE")
        listed = self.client.get("/api/returns/customer/C5").json()
        self.assertEqual(len(listed), 1)
        self.assertEqual({k: listed[0][k] for k in ("id", "orderId", "status", "amount", "date")},
                         {"id": first["returnId"], "orderId": "O-1", "status": "APPROVED", "amount": 90, "date": "2026-11-15"})
        self.assertMatches(self.evaluate("O-2"), riskScore=10, reasons=["RETURN_FREQUENCY"])
        self.assertEqual(self.client.get("/api/returns/customer/C404").status_code, 404)
