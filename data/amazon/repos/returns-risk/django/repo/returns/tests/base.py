"""Shared setup for the return/risk tests: a fresh store with linked accounts, plus helpers to add orders and past
returns and to call the API."""
import json

from django.test import SimpleTestCase

from returns import store

TODAY = "2026-11-15"


def base_customers():
    # C1 - C2 - C3 are linked in a chain; C5 has no links; C9 opened their account on 2026-11-01.
    return [
        {"id": "C1", "name": "Asha", "createdAt": "2024-01-01", "linkedAccountIds": ["C2"]},
        {"id": "C2", "name": "Bilal", "createdAt": "2024-01-01", "linkedAccountIds": ["C1", "C3"]},
        {"id": "C3", "name": "Chen", "createdAt": "2024-01-01", "linkedAccountIds": ["C2"]},
        {"id": "C5", "name": "Dev", "createdAt": "2024-01-01", "linkedAccountIds": []},
        {"id": "C9", "name": "Esha", "createdAt": "2026-11-01", "linkedAccountIds": []},
    ]


class ReturnsTestCase(SimpleTestCase):
    def setUp(self):
        self.data = {"customers": base_customers(), "orders": [], "returns": []}
        store.reset(self.data)

    def order(self, order_id, customer_id, delivered_at="2026-11-01", status="DELIVERED", category="Electronics",
              price=40, quantity=1, items=None):
        """An order with one item (id I-1) unless `items` is given."""
        self.data["orders"].append({"id": order_id, "customerId": customer_id, "status": status, "deliveredAt": delivered_at,
                                    "items": items or [{"id": "I-1", "name": "Item", "category": category, "price": price, "quantity": quantity}]})
        store.reset(self.data)

    def past_return(self, customer_id, status="APPROVED", amount=100, date="2026-10-20", order_id=None, item_id="I-1"):
        """A past return in the history."""
        n = len(self.data["returns"]) + 1
        self.data["returns"].append({"id": "R%d" % n, "customerId": customer_id, "orderId": order_id or "OLD-%d" % n,
                                     "itemId": item_id, "status": status, "amount": amount, "date": date})
        store.reset(self.data)

    def post(self, body):
        return self.client.post("/api/returns/evaluate", data=json.dumps(body), content_type="application/json")

    def evaluate(self, order_id, reason="DAMAGED", **extra):
        return self.post(dict({"orderId": order_id, "itemId": "I-1", "reason": reason, "requestedAt": TODAY}, **extra))

    def assertMatches(self, response, **expected):
        body = response.json()
        self.assertEqual({k: body.get(k) for k in expected}, expected, body)
