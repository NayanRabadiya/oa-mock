from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import store
from .rules import PRIORITIES, STATUSES
from .services.assignment import can_take
from .services.sla import is_overdue
from .services.tickets import filter_tickets, sort_tickets
from .services.workflow import can_move
from .times import is_iso_time, now


def _fail(status, message):
    return Response({"message": message}, status=status)


def _body(request):
    return request.data if isinstance(request.data, dict) else {}


@api_view(["GET", "POST"])
def tickets(request):
    """GET /api/tickets?status=&priority=&assigneeId=   POST /api/tickets {title, customer, priority, createdAt?}"""
    if request.method == "GET":
        q = request.query_params
        filters = {"status": q.get("status"), "priority": q.get("priority"), "assigneeId": q.get("assigneeId")}
        return Response(sort_tickets(filter_tickets(store.all_tickets(), filters)))
    body = _body(request)
    title, customer, priority = body.get("title"), body.get("customer"), body.get("priority")
    created_at = body.get("createdAt") or now()
    if not title or not customer or not priority:
        return _fail(400, "title, customer and priority are required")
    if priority not in PRIORITIES:
        return _fail(400, "Invalid priority")
    if not is_iso_time(created_at):
        return _fail(400, "createdAt must be a time like 2026-11-15T09:30:00Z")
    return Response(store.add_ticket({"title": title, "customer": customer, "priority": priority, "createdAt": created_at}), status=201)


@api_view(["POST"])
def assign(request, ticket_id):
    """POST /api/tickets/<id>/assign {agentId}"""
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        return _fail(404, "Ticket not found")
    agent = store.get_agent(_body(request).get("agentId"))
    if agent is None:
        return _fail(404, "Agent not found")
    if ticket["status"] not in ("open", "in_progress"):
        return _fail(409, "Only open or in-progress tickets can be assigned")
    if not can_take(agent, ticket):
        return _fail(409, "Agent has too many open tickets")
    ticket["assigneeId"] = agent["id"]
    if ticket["status"] == "open":
        ticket["status"] = "in_progress"
    return Response(ticket)


@api_view(["POST"])
def change_status(request, ticket_id):
    """POST /api/tickets/<id>/status {status, at?}"""
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        return _fail(404, "Ticket not found")
    body = _body(request)
    status, at = body.get("status"), body.get("at") or now()
    if status not in STATUSES:
        return _fail(400, "Invalid status")
    if not can_move(ticket["status"], status):
        return _fail(409, "Cannot move a ticket from %s to %s" % (ticket["status"], status))
    ticket["status"] = status
    if status == "resolved":
        ticket["resolvedAt"] = at
    elif status == "in_progress":
        ticket["resolvedAt"] = None
    return Response(ticket)


@api_view(["GET"])
def overdue(request):
    """GET /api/tickets/overdue?now="""
    at = request.query_params.get("now") or now()
    if not is_iso_time(at):
        return _fail(400, "now must be a time like 2026-11-15T09:30:00Z")
    return Response(sort_tickets([t for t in store.all_tickets() if is_overdue(t, at)]))
