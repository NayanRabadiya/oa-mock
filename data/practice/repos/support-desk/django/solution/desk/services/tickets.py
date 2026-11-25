from ..rules import PRIORITIES
from ..times import parse


def _key(ticket):
    """Most urgent first; tickets of the same priority oldest first (then by id)."""
    return (PRIORITIES.index(ticket["priority"]), parse(ticket["createdAt"]), int(ticket["id"][1:]))


def sort_tickets(tickets):
    return sorted(tickets, key=_key)


def filter_tickets(tickets, filters):
    """Keeps the tickets that match every filter given ({status, priority, assigneeId})."""
    return [t for t in tickets if all(value is None or t.get(key) == value for key, value in filters.items())]
