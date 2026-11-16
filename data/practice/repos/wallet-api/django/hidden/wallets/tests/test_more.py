"""More integrated tests (hidden in the test: they run when you submit)."""
from .base import WalletTestCase


class MoreWalletTests(WalletTestCase):
    def test_validates_amounts_and_wallets(self):
        self.assertEqual(self.deposit("W1", 0).json(), {"message": "amount must be a positive whole number"})
        self.assertEqual(self.deposit("W1", 2.5).status_code, 400)
        self.assertEqual(self.deposit("W1", "10").status_code, 400)
        self.assertEqual(self.deposit("W9", 10).json(), {"message": "Wallet not found"})
        self.assertEqual(self.wallet("W9").status_code, 404)
        self.assertEqual(self.post("/api/transfers", {"from": "W1"}).json(), {"message": "from, to and amount are required"})
        self.assertEqual(self.send("W1", "W1", 10).json(), {"message": "Cannot transfer to the same wallet"})
        self.assertEqual(self.history("W1", "?type=refund").json(), {"message": "Invalid transaction type"})
        self.assertEqual(self.history("W1", "?limit=0").status_code, 400)

    def test_cannot_spend_more_than_the_balance(self):
        self.assertEqual(self.withdraw("W2", 201).json(), {"message": "Insufficient funds"})
        self.assertEqual(self.send("W2", "W1", 201).status_code, 409)
        everything = self.withdraw("W2", 200).json()
        self.assertEqual(everything["wallet"]["balance"], 0)
        tx = everything["transaction"]
        self.assertEqual((tx["type"], tx["amount"], tx["balanceAfter"]), ("withdrawal", 200, 0))

    def test_frozen_wallets_cannot_send_or_receive(self):
        self.assertEqual(self.send("W3", "W1", 10).json(), {"message": "Wallet is frozen"})
        self.assertEqual(self.send("W1", "W3", 10).status_code, 409)
        self.assertEqual(self.deposit("W3", 10).status_code, 409)
        self.assertEqual(self.wallet("W1").json()["balance"], 1000)
        self.assertEqual(self.wallet("W3").json()["balance"], 500)

    def test_limit_caps_the_transaction_list(self):
        for i in range(1, 26):
            self.deposit("W1", i, "2026-11-15T09:%02d:00Z" % i)
        self.assertEqual(len(self.history("W1").json()), 20)
        self.assertEqual([t["amount"] for t in self.history("W1", "?limit=2").json()], [25, 24])
        self.assertEqual([t["amount"] for t in self.history("W1", "?type=deposit&limit=3").json()], [25, 24, 23])
