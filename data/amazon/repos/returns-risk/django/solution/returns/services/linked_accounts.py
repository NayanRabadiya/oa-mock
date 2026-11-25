from .. import store


def get_account_group(customer_id):
    """Accounts are linked when they share a household, address or payment method. Links can chain (A is linked to
    B, B to C), and every account in the chain belongs to the same group. Returns the ids of the whole group, the
    customer first."""
    group = [customer_id]
    seen = set(group)

    i = 0
    while i < len(group):
        customer = store.get_customer(group[i])
        for linked_id in (customer or {}).get("linkedAccountIds", []):
            if linked_id not in seen:
                seen.add(linked_id)
                group.append(linked_id)
        i += 1

    return group
