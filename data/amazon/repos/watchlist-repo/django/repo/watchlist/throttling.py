"""watchlistRateLimiter: each user may add or remove movies at most 10 times in any 2-minute window.

Adds and removes share one counter. The check runs before the view, so every add or remove request it lets
through counts, even one that then fails validation. A request it rejects (429) doesn't count.
"""
import time

from django.core.cache import cache
from rest_framework.throttling import BaseThrottle

WINDOW_SECONDS = 2 * 60
MAX_OPERATIONS = 10


def now():
    return time.time()


class WatchlistOperationThrottle(BaseThrottle):
    def allow_request(self, request, view):
        key = "watchlist-operations:%s" % request.user.pk
        history = cache.get(key, [])
        current = now()
        recent = [stamp for stamp in history if current - stamp >= WINDOW_SECONDS]
        if len(recent) >= MAX_OPERATIONS:
            cache.set(key, recent, WINDOW_SECONDS)
            return False
        recent.append(current)
        cache.set(key, recent, WINDOW_SECONDS)
        return True
