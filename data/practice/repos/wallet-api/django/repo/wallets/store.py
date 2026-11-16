"""An in-memory store standing in for the wallet database. Balances are whole rupees. reset() loads a data set
(data/seed.json when the server starts; the tests load their own)."""
_wallets = {}
_transactions = []
_next_tx = 1


def reset(data=None):
    global _wallets, _transactions, _next_tx
    data = data or {}
    _wallets = {w["id"]: dict(w) for w in data.get("wallets", [])}
    _transactions = [dict(t) for t in data.get("transactions", [])]
    _next_tx = len(_transactions) + 1


def get_wallet(wallet_id):
    return _wallets.get(wallet_id)


def transactions_of(wallet_id):
    return [t for t in _transactions if t["walletId"] == wallet_id]


def record(wallet, kind, amount, at, counterparty=None):
    """Changes a wallet's balance and records the transaction."""
    global _next_tx
    wallet["balance"] += amount if kind in ("deposit", "transfer_in") else -amount
    tx = {"id": "TX%d" % _next_tx, "walletId": wallet["id"], "type": kind, "amount": amount,
          "balanceAfter": wallet["balance"], "counterparty": counterparty, "at": at}
    _next_tx += 1
    _transactions.append(tx)
    return tx
