"""Event aggregation (pure Python)."""
from decimal import Decimal, InvalidOperation

EMAIL = "24f2001614@ds.study.iitm.ac.in"


def _amount(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        try:
            return Decimal(str(v))
        except InvalidOperation:
            return None
    if isinstance(v, str):
        try:
            return Decimal(v.strip())
        except InvalidOperation:
            return None
    return None


def aggregate(events):
    users = set()
    positive = {}  # user -> sum of positive amounts
    for e in events:
        if not isinstance(e, dict):
            continue
        user = e.get("user")
        users.add(user)
        amt = _amount(e.get("amount"))
        if amt is not None and amt > 0:
            positive[user] = positive.get(user, Decimal(0)) + amt
    revenue = sum(positive.values(), Decimal(0))
    # highest positive-amount total (ties: alphabetically first, so the answer is deterministic)
    top = min(positive.items(), key=lambda kv: (-kv[1], str(kv[0])))[0] if positive else None
    return {
        "email": EMAIL,
        "total_events": len(events),
        "unique_users": len(users),
        "revenue": round(float(revenue), 2),
        "top_user": top,
    }
