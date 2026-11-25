# Where a ticket can go from each status. A resolved ticket can be reopened (back to in_progress) or closed;
# a closed ticket is final.
NEXT = {
    "open": ["in_progress"],
    "in_progress": ["resolved", "closed"],
    "resolved": ["in_progress", "closed"],
    "closed": [],
}


def can_move(current, target):
    return target in NEXT.get(current, [])
