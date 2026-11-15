"""An in-memory store standing in for the library database. reset() loads a data set (data/seed.json when the
server starts; the tests load their own)."""
_state = {"books": {}, "members": {}, "loans": []}
_next_loan_id = 1


def reset(data=None):
    global _state, _next_loan_id
    data = data or {}
    _state = {
        "books": {b["id"]: dict(b) for b in data.get("books", [])},
        "members": {m["id"]: dict(m) for m in data.get("members", [])},
        "loans": [dict({"returnedAt": None}, **l) for l in data.get("loans", [])],
    }
    _next_loan_id = len(_state["loans"]) + 1


def all_books():
    return list(_state["books"].values())


def get_book(book_id):
    return _state["books"].get(book_id)


def get_member(member_id):
    return _state["members"].get(member_id)


def get_loan(loan_id):
    return next((l for l in _state["loans"] if l["id"] == loan_id), None)


def open_loans(keep):
    return [l for l in _state["loans"] if not l["returnedAt"] and keep(l)]


def add_loan(loan):
    global _next_loan_id
    saved = dict({"id": "L%d" % _next_loan_id, "returnedAt": None}, **loan)
    _next_loan_id += 1
    _state["loans"].append(saved)
    return saved
