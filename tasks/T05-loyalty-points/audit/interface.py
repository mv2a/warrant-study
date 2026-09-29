"""X1 (C3): the interface of `points` for valid requests.

Valid requests at the edges of the stated types are scored, not refused; the answer is one
JSON object with exactly four integer fields and total = base + bonus; a missing
bonus_categories means none; other fields in the request or in an item are ignored;
formatting of the input JSON does not matter.
"""

import json

from _cmd import finish
from _expect import expect, response

problems = []

# Valid values at the edges of the types C3 states, each with its worked-out answer.
EDGES = [
    ("no items, gold", {"tier": "gold", "items": []}, response(0, 0, 0)),
    ("no items, silver, promotion listed", {"tier": "silver", "items": [], "bonus_categories": ["lamps"]}, response(0, 0, 0)),
    ("price 0", {"tier": "gold", "items": [{"category": "seedlings", "price_cents": 0, "quantity": 9}]}, response(0, 0, 0)),
    ("quantity 1, price 1", {"tier": "standard", "items": [{"category": "twine", "price_cents": 1, "quantity": 1}]}, response(1, 0, 0)),
    ("empty bonus list", {"tier": "silver", "items": [{"category": "hoses", "price_cents": 2404, "quantity": 1}], "bonus_categories": []}, response(2404, 24, 6)),
    ("empty string in bonus list", {"tier": "standard", "items": [{"category": "hoses", "price_cents": 2404, "quantity": 1}], "bonus_categories": [""]}, response(2404, 24, 0)),
    ("single-space category", {"tier": "standard", "items": [{"category": " ", "price_cents": 700, "quantity": 2}], "bonus_categories": [" "]}, response(1400, 14, 28)),
    ("non-ASCII category", {"tier": "gold", "items": [{"category": "jardín", "price_cents": 1111, "quantity": 1}], "bonus_categories": ["jardín"]}, response(1111, 11, 27)),
    ("very large order", {"tier": "standard", "items": [{"category": "sheds", "price_cents": 987654321, "quantity": 1000}]}, response(987654321000, 9876543210, 0)),
]
for label, request, want in EDGES:
    expect(problems, label, request, want)

# bonus_categories left out means none.
plain = {"tier": "gold", "items": [{"category": "compost", "price_cents": 1845, "quantity": 3}]}
with_empty = {**plain, "bonus_categories": []}
expect(problems, "bonus_categories left out", plain, response(5535, 55, 27))
expect(problems, "bonus_categories empty", with_empty, response(5535, 55, 27))

# Other fields are ignored, in the request and in the items, even when their names or
# values look meaningful.
extras = {
    "tier": "silver",
    "member_id": "M-20417",
    "multiplier": 3,
    "cap": 10,
    "gift_card": True,
    "total_points": 999,
    "items": [
        {"category": "planters", "price_cents": 2350, "quantity": 2, "sku": "PL-9", "discount_cents": 2000, "eligible": False},
        {"category": "mulch", "price_cents": 675, "quantity": 4, "name": "bark", "quantity_unit": "bag", "category_id": 7},
    ],
    "bonus_categories": ["mulch"],
    "promo_code": "SPRING",
}
# eligible 4700 + 2700 = 7400 -> base 74; silver 92.5 -> 92 -> tier 18; mulch $27.00 -> 54.
expect(problems, "extra fields ignored", extras, response(7400, 74, 72))

# Input formatting: indentation, key order and a trailing newline do not change the answer.
request = {"bonus_categories": ["bulbs"], "items": [{"quantity": 5, "price_cents": 399, "category": "bulbs"}], "tier": "gold"}
# 1995 -> base 19; gold 28.5 -> 28 -> tier 9; bulbs $19.95 -> 38; bonus 47.
expect(problems, "pretty-printed input", None, response(1995, 19, 47), raw=json.dumps(request, indent=4) + "\n")
expect(problems, "compact input with surrounding whitespace", None, response(1995, 19, 47), raw="\n  " + json.dumps(request, separators=(",", ":")) + "  \n\n")

finish(problems, f"interface ok: {len(EDGES) + 5} valid requests")
