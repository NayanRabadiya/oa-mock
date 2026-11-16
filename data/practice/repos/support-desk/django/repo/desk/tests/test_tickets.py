"""The integrated tests for the support desk API. Run them with:  python manage.py test"""
from .base import DeskTestCase


class TicketTests(DeskTestCase):
    def test_creating_a_ticket_opens_it(self):
        res = self.create("high")
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.json(), {"id": "T1", "title": "Help", "customer": "acme", "priority": "high", "status": "open",
                                      "assigneeId": None, "createdAt": "2026-11-15T09:00:00Z", "resolvedAt": None})

    def test_tickets_are_listed_by_priority_oldest_first(self):
        self.create("low", "2026-11-15T08:00:00Z")
        self.create("high", "2026-11-15T10:00:00Z")
        self.create("urgent", "2026-11-15T11:00:00Z")
        self.create("high", "2026-11-15T09:00:00Z")
        self.assertEqual(self.ids(self.client.get("/api/tickets")), ["T3", "T4", "T2", "T1"])

    def test_an_agent_cannot_take_more_tickets_than_their_limit(self):
        for _ in range(3):
            self.create("medium")
        self.assertEqual(self.assign("T1", "A1").json()["status"], "in_progress")
        self.assertEqual(self.assign("T2", "A1").status_code, 200)
        third = self.assign("T3", "A1")
        self.assertEqual((third.status_code, third.json()), (409, {"message": "Agent has too many open tickets"}))
        self.assertEqual(self.assign("T3", "A2").status_code, 200)

    def test_tickets_move_through_the_workflow_in_order(self):
        self.create("low")
        self.assertEqual(self.move("T1", "resolved").status_code, 409)
        self.assertEqual(self.move("T1", "in_progress").status_code, 200)
        early = self.move("T1", "closed")
        self.assertEqual((early.status_code, early.json()), (409, {"message": "Cannot move a ticket from in_progress to closed"}))
        self.assertEqual(self.move("T1", "resolved").status_code, 200)
        self.assertEqual(self.move("T1", "closed").json()["status"], "closed")

    def test_a_ticket_is_overdue_only_after_its_SLA(self):
        self.create("high", "2026-11-14T10:00:00Z")      # 23 hours before the check
        self.create("high", "2026-11-14T08:00:00Z")      # 25 hours before
        self.create("urgent", "2026-11-15T05:30:00Z")    # 3.5 hours before
        res = self.client.get("/api/tickets/overdue?now=2026-11-15T09:00:00Z")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.ids(res), ["T2"])
