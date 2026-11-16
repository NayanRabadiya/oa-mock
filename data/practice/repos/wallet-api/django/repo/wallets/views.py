from functools import wraps

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .limits import DEFAULT_PAGE, MAX_PAGE, TYPES
from .services import wallet as wallets
from .services.errors import WalletError
from .services.transfers import transfer
from .times import is_iso_time, now


def handle(fn):
    """Turns a WalletError into its HTTP answer."""
    @wraps(fn)
    def run(request, *args, **kwargs):
        try:
            return fn(request, *args, **kwargs)
        except WalletError as e:
            return Response({"message": e.message}, status=e.status)
    return run


def _body(request):
    return request.data if isinstance(request.data, dict) else {}


def _time(body):
    at = body.get("at") or now()
    if not is_iso_time(at):
        raise WalletError(400, "at must be a time like 2026-11-15T09:30:00Z")
    return at


@api_view(["GET"])
@handle
def get_wallet(request, wallet_id):
    """GET /api/wallets/<id>"""
    return Response(wallets.wallet_or_fail(wallet_id))


@api_view(["POST"])
@handle
def deposit(request, wallet_id):
    """POST /api/wallets/<id>/deposit {amount, at?}"""
    body = _body(request)
    return Response(wallets.deposit(wallet_id, body.get("amount"), _time(body)))


@api_view(["POST"])
@handle
def withdraw(request, wallet_id):
    """POST /api/wallets/<id>/withdraw {amount, at?}"""
    body = _body(request)
    return Response(wallets.withdraw(wallet_id, body.get("amount"), _time(body)))


@api_view(["POST"])
@handle
def create_transfer(request):
    """POST /api/transfers {from, to, amount, at?}"""
    body = _body(request)
    return Response(transfer(body.get("from"), body.get("to"), body.get("amount"), _time(body)), status=201)


@api_view(["GET"])
@handle
def transactions(request, wallet_id):
    """GET /api/wallets/<id>/transactions?type=&limit="""
    kind = request.query_params.get("kind")
    raw = request.query_params.get("limit")
    if kind is not None and kind not in TYPES:
        raise WalletError(400, "Invalid transaction type")
    if raw is not None and not raw.isdigit():
        raise WalletError(400, "limit must be between 1 and %d" % MAX_PAGE)
    limit = DEFAULT_PAGE if raw is None else int(raw)
    if not 1 <= limit <= MAX_PAGE:
        raise WalletError(400, "limit must be between 1 and %d" % MAX_PAGE)
    return Response(wallets.history(wallet_id, kind, limit))
