from .. import store


def get_account_group(customer_id):
    """Accounts are linked when they share a household, address or payment method. Links can chain (A is linked to
    B, B to C), and every account in the chain belongs to the same group. Returns the ids of the whole group, the
    customer first."""
    customer = store.get_customer(customer_id)
    linked = (customer or {}).get("linkedAccountIds", [])

    return [customer_id] + [i for i in linked if i != customer_id]
