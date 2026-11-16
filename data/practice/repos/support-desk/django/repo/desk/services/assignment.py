from .. import store

ACTIVE = ("open",)


def workload(agent_id, except_id=None):
    """How many unfinished tickets an agent has, not counting `except_id`."""
    return sum(1 for t in store.all_tickets()
               if t["assigneeId"] == agent_id and t["id"] != except_id and t["status"] in ACTIVE)


def can_take(agent, ticket):
    """An agent can take a ticket while they have fewer than maxOpen unfinished tickets."""
    return workload(agent["id"], ticket["id"]) < agent["maxOpen"]
