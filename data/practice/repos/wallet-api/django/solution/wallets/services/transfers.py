from .. import store
from .errors import WalletError
from .wallet import active_or_fail, is_amount, wallet_or_fail


def transfer(from_id, to_id, amount, at):
    """Moves money between two wallets. Either both sides change or neither does: every check runs before any
    balance changes."""
    if not from_id or not to_id or amount is None:
        raise WalletError(400, "from, to and amount are required")
    if not is_amount(amount):
        raise WalletError(400, "amount must be a positive whole number")
    if from_id == to_id:
        raise WalletError(400, "Cannot transfer to the same wallet")

    source = wallet_or_fail(from_id)
    target = wallet_or_fail(to_id)
    active_or_fail(source)
    active_or_fail(target)
    if source["balance"] < amount:
        raise WalletError(409, "Insufficient funds")

    store.record(source, "transfer_out", amount, at, target["id"])
    store.record(target, "transfer_in", amount, at, source["id"])
    return {"from": source, "to": target, "amount": amount}
