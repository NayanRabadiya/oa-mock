"""The integrated tests for the wallet API. Run them with:  python manage.py test"""
from .base import WalletTestCase


class WalletTests(WalletTestCase):
    def test_a_deposit_adds_to_the_balance(self):
        res = self.deposit("W1", 250)
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json()["wallet"], {"id": "W1", "owner": "Asha", "balance": 1250, "status": "active"})
        self.assertEqual(res.json()["transaction"], {"id": "TX1", "walletId": "W1", "type": "deposit", "amount": 250,
                                                     "balanceAfter": 1250, "counterparty": None, "at": "2026-11-15T09:00:00Z"})

    def test_a_transfer_moves_money_between_wallets(self):
        res = self.send("W1", "W2", 300)
        self.assertEqual(res.status_code, 201, res.content)
        body = res.json()
        self.assertEqual((body["amount"], body["from"]["balance"], body["to"]["balance"]), (300, 700, 500))
        self.assertEqual(self.wallet("W2").json()["balance"], 500)

    def test_a_failed_transfer_changes_nothing(self):
        res = self.send("W1", "W404", 300)
        self.assertEqual((res.status_code, res.json()), (404, {"message": "Wallet not found"}))
        self.assertEqual(self.wallet("W1").json()["balance"], 1000)
        self.assertEqual(self.history("W1").json(), [])

    def test_lists_a_wallets_transactions_newest_first(self):
        self.deposit("W1", 100, "2026-11-15T08:00:00Z")
        self.deposit("W1", 50, "2026-11-15T11:00:00Z")
        self.deposit("W2", 70, "2026-11-15T09:00:00Z")
        res = self.history("W1")
        self.assertEqual(res.status_code, 200, res.content[:300])
        self.assertEqual([(t["id"], t["amount"], t["balanceAfter"]) for t in res.json()], [("TX2", 50, 1150), ("TX1", 100, 1100)])

    def test_filters_transactions_by_type(self):
        self.deposit("W2", 100, "2026-11-15T08:00:00Z")
        self.send("W2", "W1", 50, "2026-11-15T09:00:00Z")
        self.send("W1", "W2", 20, "2026-11-15T10:00:00Z")
        res = self.history("W2", "?type=transfer_out")
        self.assertEqual(res.status_code, 200, res.content[:300])
        self.assertEqual([(t["type"], t["amount"], t["counterparty"]) for t in res.json()], [("transfer_out", 50, "W1")])
        self.assertEqual([t["amount"] for t in self.history("W2", "?type=transfer_in").json()], [20])
