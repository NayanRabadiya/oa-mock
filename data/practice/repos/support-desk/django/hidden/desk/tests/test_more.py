"""More integrated tests (hidden in the test: they run when you submit)."""
from .base import DeskTestCase


class MoreTicketTests(DeskTestCase):
    def test_validates_the_request(self):
        self.assertEqual(self.post("/api/tickets", {"title": "x"}).json(), {"message": "title, customer and priority are required"})
        self.assertEqual(self.create("critical").json(), {"message": "Invalid priority"})
        self.assertEqual(self.create("low", "15/11/2026").status_code, 400)
        self.assertEqual(self.assign("T9", "A1").json(), {"message": "Ticket not found"})
        self.create("low")
        self.assertEqual(self.assign("T1", "A9").json(), {"message": "Agent not found"})
        self.assertEqual(self.move("T1", "done").json(), {"message": "Invalid status"})

    def test_filters_by_status_priority_and_assignee(self):
        self.create("low")
        self.create("high")
        self.create("high")
        self.assign("T2", "A1")
        self.assertEqual(self.ids(self.client.get("/api/tickets?priority=high")), ["T2", "T3"])
        self.assertEqual(self.ids(self.client.get("/api/tickets?status=open")), ["T3", "T1"])
        self.assertEqual(self.ids(self.client.get("/api/tickets?assigneeId=A1&status=in_progress")), ["T2"])
        self.assertEqual(self.client.get("/api/tickets?assigneeId=A2").json(), [])

    def test_resolving_records_when_reopening_clears_it(self):
        self.create("medium")
        self.move("T1", "in_progress")
        self.assertEqual(self.move("T1", "resolved", "2026-11-15T13:00:00Z").json()["resolvedAt"], "2026-11-15T13:00:00Z")
        reopened = self.move("T1", "in_progress").json()
        self.assertEqual((reopened["status"], reopened["resolvedAt"]), ("in_progress", None))
        self.move("T1", "resolved")
        self.move("T1", "closed")
        self.assertEqual(self.move("T1", "in_progress").status_code, 409)
        self.assertEqual(self.assign("T1", "A1").json(), {"message": "Only open or in-progress tickets can be assigned"})

    def test_finished_tickets_are_never_overdue_and_do_not_count_toward_an_agent_limit(self):
        for _ in range(3):
            self.create("urgent", "2026-11-10T00:00:00Z")
        self.assign("T1", "A1")
        self.assign("T2", "A1")
        self.move("T1", "resolved")
        self.assertEqual(self.ids(self.client.get("/api/tickets/overdue?now=2026-11-15T09:00:00Z")), ["T2", "T3"])
        self.assertEqual(self.assign("T3", "A1").status_code, 200)
