from .. import risk_rules as rules
from ..dates import days_between


def score_return(item, reason, customer, history, requested_at):
    """Adds up the risk points for one return. Returns (score, reasons) where reasons are the codes of every rule
    that added points, in this order: return reason, value, history, refund total, account age."""
    score = 0
    reasons = []

    reason_points = rules.REASON_POINTS.get(reason, 0)
    if reason_points > 0:
        score += reason_points
        reasons.append("REASON_NOT_AS_DESCRIBED" if reason == "NOT_AS_DESCRIBED" else "REASON_DISCRETIONARY")

    value = float(item["price"]) * int(item.get("quantity") or 1)
    tier = next((t for t in rules.VALUE_TIERS if value >= t["min"]), None)
    if tier:
        score += tier["points"]
        reasons.append(tier["code"])

    if history["count"] > 0:
        score += min(history["count"] * rules.POINTS_PER_RECENT_RETURN, rules.MAX_HISTORY_POINTS)
        reasons.append("RETURN_FREQUENCY")

    if history["total"] > rules.REFUND_TOTAL_LIMIT:
        score += rules.REFUND_TOTAL_POINTS
        reasons.append("REFUND_TOTAL_HIGH")

    if customer.get("createdAt") and days_between(customer["createdAt"], requested_at) < rules.NEW_ACCOUNT_DAYS:
        score += rules.NEW_ACCOUNT_POINTS
        reasons.append("NEW_ACCOUNT")

    return min(score, rules.MAX_SCORE), reasons
