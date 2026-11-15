from .. import store
from ..dates import days_between
from ..policy import get_policy


def check_eligibility(order, item, requested_at):
    """The first rule a return request breaks, as a reason code, or None when it may be returned.

    Rules are checked in this order: delivered, not already returned, returnable category, inside the window.
    """
    if order.get("status") != "DELIVERED" or not order.get("deliveredAt"):
        return "NOT_DELIVERED"

    previous = store.returns_for_item(order["id"], item["id"])
    if any(r["status"] in ("APPROVED", "PENDING_REVIEW") for r in previous):
        return "ALREADY_RETURNED"

    policy = get_policy(item.get("category"))
    if not policy["returnable"]:
        return "NON_RETURNABLE_CATEGORY"

    days_since_delivery = days_between(order["deliveredAt"], requested_at)
    if days_since_delivery >= policy["window_days"]:
        return "RETURN_WINDOW_EXPIRED"

    return None
