import logging

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import store
from .dates import is_iso_date, today
from .risk_rules import REASON_POINTS
from .services.decisions import STATUS_FOR, decide, ineligible
from .services.eligibility import check_eligibility
from .services.history import summarize
from .services.linked_accounts import get_account_group
from .services.risk_scoring import score_return

logger = logging.getLogger("returns")


def error(message, code):
    return Response({"message": message}, status=code)


@api_view(["POST"])
def evaluate_return(request):
    """POST /api/returns/evaluate  {orderId, itemId, reason, requestedAt?}"""
    try:
        body = request.data if isinstance(request.data, dict) else {}
        order_id, item_id, reason = body.get("orderId"), body.get("itemId"), body.get("reason")
        requested_at = body.get("requestedAt", today())

        if not order_id or not item_id or not reason:
            return error("orderId, itemId and reason are required", status.HTTP_400_BAD_REQUEST)
        if reason not in REASON_POINTS:
            return error("Invalid return reason", status.HTTP_400_BAD_REQUEST)
        if not is_iso_date(requested_at):
            return error("requestedAt must be a date like 2026-11-15", status.HTTP_400_BAD_REQUEST)

        order = store.get_order(order_id)
        if order is None:
            return error("Order not found", status.HTTP_404_NOT_FOUND)
        item = next((i for i in order.get("items", []) if i["id"] == item_id), None)
        if item is None:
            return error("Item not found in order", status.HTTP_404_NOT_FOUND)
        customer = store.get_customer(order["customerId"]) or {"id": order["customerId"]}

        blocked = check_eligibility(order, item, requested_at)
        if blocked:
            result = ineligible(blocked)
        else:
            group = get_account_group(customer["id"])
            history = summarize(group, requested_at)
            score, reasons = score_return(item, reason, customer, history, requested_at)
            result = decide(score, reasons)

        record = store.add_return({
            "customerId": customer["id"],
            "orderId": order_id,
            "itemId": item_id,
            "status": STATUS_FOR[result["decision"]],
            "amount": float(item["price"]) * int(item.get("quantity") or 1),
            "date": requested_at,
            "reason": reason,
        })
        return Response(dict({"returnId": record["id"]}, **result))
    except Exception:
        logger.exception("Evaluate return error")
        return error("Server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def customer_returns(request, customer_id):
    """GET /api/returns/customer/<customerId>  every return request of one customer, oldest first"""
    if store.get_customer(customer_id) is None:
        return error("Customer not found", status.HTTP_404_NOT_FOUND)
    return Response(store.returns_for_customer(customer_id))
