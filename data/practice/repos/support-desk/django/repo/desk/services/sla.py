from ..rules import SLA_HOURS
from ..times import SECONDS_PER_HOUR, parse

UNFINISHED = ("open", "in_progress")


def hours_open(ticket, now):
    return (parse(now) - parse(ticket["createdAt"])).total_seconds() / 60


def is_overdue(ticket, now):
    """A ticket is overdue when it is still unfinished more than SLA_HOURS[priority] hours after it was created."""
    return ticket["status"] in UNFINISHED and hours_open(ticket, now) > SLA_HOURS[ticket["priority"]]
