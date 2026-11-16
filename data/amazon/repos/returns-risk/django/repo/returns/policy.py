"""Which product categories can be returned, and within how many days of delivery.

Orders store the category the way the catalogue shows it ("Electronics", "Home & Kitchen" ...); policy keys are
lowercase.
"""
RETURN_POLICY = {
    "electronics": {"returnable": True, "window_days": 30},
    "apparel": {"returnable": True, "window_days": 45},
    "home & kitchen": {"returnable": True, "window_days": 30},
    "books": {"returnable": True, "window_days": 14},
    "jewelry": {"returnable": True, "window_days": 15},
    "grocery": {"returnable": False, "window_days": 0},
    "digital content": {"returnable": False, "window_days": 0},
    "gift cards": {"returnable": False, "window_days": 0},
}

# Unknown categories can't be returned.
NOT_RETURNABLE = {"returnable": False, "window_days": 0}


def get_policy(category):
    key = str(category or "").strip()
    return RETURN_POLICY.get(key, NOT_RETURNABLE)
