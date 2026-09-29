"""Shared helpers for the X (audit) checks, written from intent.md alone.

`expected` is an independent model of the promises, used for generated cases.
Hand-written checks compare against literal numbers worked out from the intent.
"""

from _cmd import call

FIELDS = ("eligible_cents", "base_points", "bonus_points", "total_points")
# G2: multiplier as an exact fraction, so rounding down is integer division.
TIERS = {"standard": (1, 1), "silver": (5, 4), "gold": (3, 2)}
GIFT_CARD = "gift_card"  # C1
CAP = 500  # C2


def expected(request):
    """The response the intent promises for a valid request."""
    eligible = [item for item in request["items"] if item["category"] != GIFT_CARD]
    eligible_cents = sum(item["price_cents"] * item["quantity"] for item in eligible)
    base = eligible_cents // 100
    num, den = TIERS[request["tier"]]
    tier_bonus = base * num // den - base
    promoted = set(request.get("bonus_categories", []))
    promoted_cents = sum(item["price_cents"] * item["quantity"] for item in eligible if item["category"] in promoted)
    category_bonus = 2 * (promoted_cents // 100)
    bonus = min(CAP, tier_bonus + category_bonus)
    return {"eligible_cents": eligible_cents, "base_points": base, "bonus_points": bonus, "total_points": base + bonus}


def response(eligible_cents, base, bonus):
    return {"eligible_cents": eligible_cents, "base_points": base, "bonus_points": bonus, "total_points": base + bonus}


def shape_problem(body):
    """Why a success body breaks C3's output shape, or None."""
    if not isinstance(body, dict) or set(body) != set(FIELDS):
        return f"expected an object with exactly {list(FIELDS)}, got {body!r}"
    if not all(type(body[field]) is int for field in FIELDS):
        return f"every field must be an integer, got {body!r}"
    if body["total_points"] != body["base_points"] + body["bonus_points"]:
        return f"total_points must equal base_points plus bonus_points, got {body!r}"
    return None


def short(value, limit=150):
    text = value if isinstance(value, str) else repr(value)
    return text if len(text) <= limit else text[: limit - 3] + "..."


def expect(problems, label, request, want, raw=None):
    """Call the command and record a problem unless it answers exactly `want` with status 0."""
    status, body = call(request, raw=raw)
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0 and {want}")
        return None
    bad = shape_problem(body)
    if bad:
        problems.append(f"{label}: {short(bad)}")
    elif body != want:
        problems.append(f"{label}: expected {want}, got {body}")
    return body


def refuse(problems, label, request=None, raw=None):
    """Call the command and record a problem unless it exits 2 with nothing on standard output."""
    status, body = call(request, raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected refusal (status 2, no output), got status {status} and {short(body, 80)}")
