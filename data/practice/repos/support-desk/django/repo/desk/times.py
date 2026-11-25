"""Times are ISO 8601 strings in UTC, like 2026-11-15T09:30:00Z."""
import re
from datetime import datetime, timezone

ISO_TIME = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?Z$")
SECONDS_PER_HOUR = 60 * 60


def parse(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def is_iso_time(value):
    if not isinstance(value, str) or not ISO_TIME.match(value):
        return False
    try:
        parse(value)
        return True
    except ValueError:
        return False


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
