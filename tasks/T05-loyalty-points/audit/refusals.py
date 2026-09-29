"""X2 (C3, C4): every kind of invalid request C4 lists is refused with status 2 and no output.

The bad value is placed in the first, a middle or the last item, and on gift cards too,
since gift cards are still items and must be valid.
"""

import copy

from _cmd import finish
from _expect import refuse

problems = []
count = 0
DROP = object()


def check(label, request=None, raw=None):
    global count
    count += 1
    refuse(problems, label, request=request, raw=raw)


GOOD = {
    "tier": "silver",
    "items": [
        {"category": "pruners", "price_cents": 1675, "quantity": 2},
        {"category": "gift_card", "price_cents": 2500, "quantity": 1},
        {"category": "fertiliser", "price_cents": 899, "quantity": 3},
    ],
    "bonus_categories": ["pruners"],
}


def with_(**changes):
    request = copy.deepcopy(GOOD)
    for key, value in changes.items():
        if value is DROP:
            request.pop(key)
        else:
            request[key] = value
    return request


def with_item(index, **changes):
    request = copy.deepcopy(GOOD)
    item = request["items"][index]
    for key, value in changes.items():
        if value is DROP:
            item.pop(key)
        else:
            item[key] = value
    return request


# Input that is not a JSON object.
for label, raw in [
    ("empty input", ""),
    ("whitespace only", "  \n\t\n"),
    ("plain text", "gold member, 3 items"),
    ("truncated object", '{"tier": "gold", "items": ['),
    ("single-quoted pseudo-JSON", "{'tier': 'gold', 'items': []}"),
    ("JSON list", "[]"),
    ("list holding a valid request", '[{"tier": "gold", "items": []}]'),
    ("JSON string", '"gold"'),
    ("JSON number", "4200"),
    ("JSON null", "null"),
    ("JSON true", "true"),
    ("two objects in a row", '{"tier": "gold", "items": []}{"tier": "gold", "items": []}'),
]:
    check(label, raw=raw)

# Tier missing or not exactly one of the three names.
check("tier missing", with_(tier=DROP))
for bad in [None, "", "Gold", "GOLD", "Silver", " standard", "gold ", "platinum", "bronze", "std", 1, 1.5, True, False, ["gold"], {"name": "gold"}]:
    check(f"tier {bad!r}", with_(tier=bad))

# Items missing or not a list.
check("items missing", with_(items=DROP))
for bad in [None, "[]", {}, {"category": "pruners", "price_cents": 1675, "quantity": 2}, 3, True]:
    check(f"items {bad!r}", with_(items=bad))

# An item that is not an object.
for bad in [None, "pruners", 1675, True, ["pruners", 1675, 2], []]:
    request = copy.deepcopy(GOOD)
    request["items"][1] = bad
    check(f"middle item {bad!r}", request)

# An item that lacks one of its three fields (first, gift card, last).
for index in (0, 1, 2):
    for field in ("category", "price_cents", "quantity"):
        check(f"item {index} without {field}", with_item(index, **{field: DROP}))
request = copy.deepcopy(GOOD)
request["items"].append({})
check("an empty item object", request)

# A category that is not a non-empty string.
for bad in ["", None, 7, 0, True, ["pruners"], {"name": "pruners"}]:
    check(f"category {bad!r}", with_item(2, category=bad))

# A price that is negative, fractional, text or true/false, a whole value with a decimal
# point (and other non-integers).
for bad in [-1, -1675, 16.75, 0.5, -0.5, 1675.0, 0.0, "1675", "16.75", "", True, False, None, [1675], {"cents": 1675}]:
    check(f"price {bad!r}", with_item(0, price_cents=bad))
check("gift card with a negative price", with_item(1, price_cents=-2500))
check("gift card with a text price", with_item(1, price_cents="2500"))

# A quantity below 1, fractional, text or true/false, a whole value with a decimal point
# (and other non-integers).
for bad in [0, -1, -4, 1.5, 0.5, 2.25, 3.0, 1.0, "2", "one", True, False, None, [2]]:
    check(f"quantity {bad!r}", with_item(2, quantity=bad))
check("gift card with quantity 0", with_item(1, quantity=0))
check("gift card with quantity true", with_item(1, quantity=True))

# C4: a whole value written with a decimal point or an exponent is still refused.
check("price written as 25e2", raw='{"tier": "standard", "items": [{"category": "pruners", "price_cents": 25e2, "quantity": 1}]}')
check("quantity written as 1E0", raw='{"tier": "gold", "items": [{"category": "pruners", "price_cents": 1675, "quantity": 1E0}]}')
check("gift card price written as 2500.00", raw='{"tier": "silver", "items": [{"category": "gift_card", "price_cents": 2500.00, "quantity": 1}]}')

# bonus_categories present but not a list of strings.
for bad in [None, "pruners", {"pruners": True}, 5, True, [1], ["pruners", None], ["pruners", 2], [["pruners"]], [True], [{"name": "pruners"}]]:
    check(f"bonus_categories {bad!r}", with_(bonus_categories=bad))

# A standard member with only gift cards is still refused when one field is bad.
check("gift-card-only order with a fractional quantity", {"tier": "standard", "items": [{"category": "gift_card", "price_cents": 5000, "quantity": 1.5}]})

finish(problems, f"refusals ok: {count} invalid requests")
