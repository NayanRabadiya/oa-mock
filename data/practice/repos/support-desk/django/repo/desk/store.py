"""An in-memory store standing in for the help desk database. reset() loads a data set (data/seed.json when the
server starts; the tests load their own)."""
_agents = {}
_tickets = []
_next_id = 1


def reset(data=None):
    global _agents, _tickets, _next_id
    data = data or {}
    _agents = {a["id"]: dict(a) for a in data.get("agents", [])}
    _tickets = [dict({"assigneeId": None, "resolvedAt": None}, **t) for t in data.get("tickets", [])]
    _next_id = len(_tickets) + 1


def get_agent(agent_id):
    return _agents.get(agent_id)


def all_tickets():
    return list(_tickets)


def get_ticket(ticket_id):
    return next((t for t in _tickets if t["id"] == ticket_id), None)


def add_ticket(ticket):
    global _next_id
    saved = dict({"id": "T%d" % _next_id, "status": "open", "assigneeId": None, "resolvedAt": None}, **ticket)
    saved = {k: saved[k] for k in ("id", "title", "customer", "priority", "status", "assigneeId", "createdAt", "resolvedAt")}
    _next_id += 1
    _tickets.append(saved)
    return saved
