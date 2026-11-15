from .. import store
from ..loan_rules import MAX_OPEN_LOANS


def available_copies(book):
    """How many copies of a book are on the shelf right now."""
    return book["copies"] - len(store.open_loans(lambda l: l["bookId"] == book["id"]))


def cannot_borrow(member, book):
    """Why a member can't borrow a book right now, or None when they can."""
    if available_copies(book) <= 0:
        return "No copies available"
    open_loans = store.open_loans(lambda l: l["memberId"] == member["id"])
    if len(open_loans) > MAX_OPEN_LOANS:
        return "Loan limit reached"
    return None
