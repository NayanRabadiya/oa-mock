"""An in-memory store standing in for the customer, order and returns databases.

reset() loads a data set (data/seed.json when the server starts; the tests load their own).
"""
import copy

_state = {"customers": {}, "orders": {}, "returns": []}
_next_id = [1]


def reset(data=None):
    data = data or {}
    _state["customers"] = {c["id"]: dict({"linkedAccountIds": []}, **c) for c in data.get("customers", [])}
    _state["orders"] = {o["id"]: copy.deepcopy(o) for o in data.get("orders", [])}
    _state["returns"] = [dict(r) for r in data.get("returns", [])]
    _next_id[0] = len(_state["returns"]) + 1


def get_customer(customer_id):
    return _state["customers"].get(customer_id)


def get_order(order_id):
    return _state["orders"].get(order_id)


def returns_for_customer(customer_id):
    return [r for r in _state["returns"] if r["customerId"] == customer_id]


def returns_for_item(order_id, item_id):
    return [r for r in _state["returns"] if r["orderId"] == order_id and r["itemId"] == item_id]


def add_return(record):
    saved = dict({"id": "RET-%04d" % _next_id[0]}, **record)
    _next_id[0] += 1
    _state["returns"].append(saved)
    return saved
