from ..risk_rules import MANUAL_REVIEW_FROM, REJECT_FROM
from .reason_codes import messages_for

# What the service decides, and what it stores in the return history for that decision.
STATUS_FOR = {"AUTO_APPROVE": "APPROVED", "MANUAL_REVIEW": "PENDING_REVIEW", "REJECT": "REJECTED"}


def decide(score, reasons):
    decision = "AUTO_APPROVE"
    codes = list(reasons)

    if score >= REJECT_FROM:
        decision = "REJECT"
        codes.append("HIGH_RISK")
    elif score >= MANUAL_REVIEW_FROM:
        decision = "MANUAL_REVIEW"

    return {"decision": decision, "riskScore": score, "reasons": codes, "messages": messages_for(codes)}


def ineligible(code):
    """A request that breaks an eligibility rule is rejected with just that reason."""
    return {"decision": "REJECT", "riskScore": 0, "reasons": [code], "messages": messages_for([code])}
