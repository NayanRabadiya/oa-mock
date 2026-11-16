from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import store
from .dates import is_iso_date, today
from .services.fees import late_fee
from .services.loans import available_copies, cannot_borrow


def _error(status, message):
    return Response({"message": message}, status=status)


@api_view(["GET"])
def list_books(request):
    """GET /api/books  every book, with how many copies are on the shelf"""
    return Response([dict(b, available=available_copies(b)) for b in store.all_books()])


@api_view(["POST"])
def borrow_book(request):
    """POST /api/loans  {memberId, bookId, borrowedAt?}"""
    body = request.data if isinstance(request.data, dict) else {}
    member_id, book_id = body.get("memberId"), body.get("bookId")
    borrowed_at = body.get("borrowedAt") or today()
    if not member_id or not book_id:
        return _error(400, "memberId and bookId are required")
    if not is_iso_date(borrowed_at):
        return _error(400, "borrowedAt must be a date like 2026-11-15")
    member = store.get_member(member_id)
    if member is None:
        return _error(404, "Member not found")
    book = store.get_book(book_id)
    if book is None:
        return _error(404, "Book not found")
    problem = cannot_borrow(member, book)
    if problem:
        return _error(409, problem)
    return Response(store.add_loan({"memberId": member_id, "bookId": book_id, "borrowedAt": borrowed_at}), status=201)


@api_view(["POST"])
def return_book(request, loan_id):
    """POST /api/loans/<loan_id>/return  {returnedAt?}"""
    loan = store.get_loan(loan_id)
    if loan is None:
        return _error(404, "Loan not found")
    if loan["returnedAt"]:
        return _error(409, "Loan already returned")
    body = request.data if isinstance(request.data, dict) else {}
    returned_at = body.get("returnedAt") or today()
    if not is_iso_date(returned_at):
        return _error(400, "returnedAt must be a date like 2026-11-15")
    loan["returnedAt"] = returned_at
    return Response(dict({"loanId": loan["id"], "returnedAt": returned_at}, **late_fee(loan["borrowedAt"], returned_at)))
