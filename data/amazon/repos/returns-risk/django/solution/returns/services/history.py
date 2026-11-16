from .. import store
from ..dates import days_between
from ..risk_rules import HISTORY_DAYS


def recent_refunds(account_ids, requested_at):
    """Approved (refunded) returns of a group of accounts in the HISTORY_DAYS days before `requested_at`."""
    refunds = []
    for account_id in account_ids:
        for ret in store.returns_for_customer(account_id):
            age = days_between(ret["date"], requested_at)
            if ret["status"] == "APPROVED" and 0 <= age <= HISTORY_DAYS:
                refunds.append(ret)
    return refunds


def summarize(account_ids, requested_at):
    refunds = recent_refunds(account_ids, requested_at)
    return {"count": len(refunds), "total": sum(float(r.get("amount") or 0) for r in refunds)}
