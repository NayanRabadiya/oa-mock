"""Shared setup for the wallet tests: three wallets, no transactions yet."""
import json

from django.test import SimpleTestCase

from wallets import store


class WalletTestCase(SimpleTestCase):
    def setUp(self):
        store.reset({"wallets": [{"id": "W1", "owner": "Asha", "balance": 1000, "status": "active"},
                                 {"id": "W2", "owner": "Bilal", "balance": 200, "status": "active"},
                                 {"id": "W3", "owner": "Chen", "balance": 500, "status": "frozen"}],
                     "transactions": []})

    def post(self, url, body):
        return self.client.post(url, data=json.dumps(body), content_type="application/json")

    def deposit(self, wallet_id, amount, at="2026-11-15T09:00:00Z"):
        return self.post("/api/wallets/%s/deposit" % wallet_id, {"amount": amount, "at": at})

    def withdraw(self, wallet_id, amount, at="2026-11-15T09:00:00Z"):
        return self.post("/api/wallets/%s/withdraw" % wallet_id, {"amount": amount, "at": at})

    def send(self, source, target, amount, at="2026-11-15T10:00:00Z"):
        return self.post("/api/transfers", {"from": source, "to": target, "amount": amount, "at": at})

    def wallet(self, wallet_id):
        return self.client.get("/api/wallets/%s" % wallet_id)

    def history(self, wallet_id, query=""):
        return self.client.get("/api/wallets/%s/transactions%s" % (wallet_id, query))
