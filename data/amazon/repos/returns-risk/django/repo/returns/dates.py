"""Dates are calendar days, written "YYYY-MM-DD"."""
import datetime
import re

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_iso_date(value):
    if not isinstance(value, str) or not ISO_DATE.match(value):
        return False
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def days_between(start, end):
    """Whole days from `start` to `end` (negative when `end` is earlier)."""
    return (datetime.date.fromisoformat(str(end)[:10]) - datetime.date.fromisoformat(str(start)[:10])).days


def today():
    return datetime.date.today().isoformat()
