"""Shared setup for the support desk tests: two agents and no tickets."""
import json

from django.test import SimpleTestCase

from desk import store


class DeskTestCase(SimpleTestCase):
    def setUp(self):
        store.reset({"agents": [{"id": "A1", "name": "Meera", "maxOpen": 2}, {"id": "A2", "name": "Tomas", "maxOpen": 3}],
                     "tickets": []})

    def post(self, url, body):
        return self.client.post(url, data=json.dumps(body), content_type="application/json")

    def create(self, priority, created_at="2026-11-15T09:00:00Z", title="Help"):
        return self.post("/api/tickets", {"title": title, "customer": "acme", "priority": priority, "createdAt": created_at})

    def assign(self, ticket_id, agent_id):
        return self.post("/api/tickets/%s/assign" % ticket_id, {"agentId": agent_id})

    def move(self, ticket_id, status, at="2026-11-15T12:00:00Z"):
        return self.post("/api/tickets/%s/status" % ticket_id, {"status": status, "at": at})

    def ids(self, response):
        return [t["id"] for t in response.json()]
