import re

OBJECT_ID = re.compile(r"^[0-9a-fA-F]{24}$")


def is_valid_movie_id(value):
    """Movie ids are 24 hexadecimal characters, like MongoDB ObjectIds."""
    return isinstance(value, str) and bool(OBJECT_ID.match(value))
