from .. import store
from ..times import parse
from .errors import WalletError


def is_amount(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def wallet_or_fail(wallet_id):
    wallet = store.get_wallet(wallet_id)
    if wallet is None:
        raise WalletError(404, "Wallet not found")
    return wallet


def active_or_fail(wallet):
    if wallet["status"] != "active":
        raise WalletError(409, "Wallet is frozen")


def deposit(wallet_id, amount, at):
    if not is_amount(amount):
        raise WalletError(400, "amount must be a positive whole number")
    wallet = wallet_or_fail(wallet_id)
    active_or_fail(wallet)
    return {"wallet": wallet, "transaction": store.record(wallet, "deposit", amount, at)}


def withdraw(wallet_id, amount, at):
    if not is_amount(amount):
        raise WalletError(400, "amount must be a positive whole number")
    wallet = wallet_or_fail(wallet_id)
    active_or_fail(wallet)
    if wallet["balance"] < amount:
        raise WalletError(409, "Insufficient funds")
    return {"wallet": wallet, "transaction": store.record(wallet, "withdrawal", amount, at)}


def history(wallet_id, kind, limit):
    """Newest first (then the later transaction first)."""
    wallet_or_fail(wallet_id)
    txs = [t for t in store.transactions_of(wallet_id) if not kind or t["type"] == kind]
    txs.sort(key=lambda t: (parse(t["at"]), int(t["id"][2:])), reverse=True)
    return txs[:limit]
