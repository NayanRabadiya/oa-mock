from ..dates import days_between
from ..loan_rules import FEE_PER_DAY, LOAN_DAYS, MAX_FEE


def late_fee(borrowed_at, returned_at):
    """Days a return is late, and the fee for it. A book returned on its due date (day 14) is on time."""
    days_late = max(0, days_between(borrowed_at, returned_at))
    return {"daysLate": days_late, "fee": min(days_late * FEE_PER_DAY, MAX_FEE)}
