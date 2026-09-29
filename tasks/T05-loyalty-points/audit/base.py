"""X3 (G1): base points are the whole dollars of eligible spend, floored once on the order total.

Eligible spend is price times quantity summed over the non-gift-card items. Standard members
with nothing promoted get no bonus, so the whole answer is fixed by G1; a few silver and
gold orders confirm the tier leaves base_points and eligible_cents alone.
"""

from _cmd import finish
from _expect import expect, response


def item(category, price, quantity=1):
    return {"category": category, "price_cents": price, "quantity": quantity}


# (label, items, eligible_cents, base_points) for standard members with nothing promoted.
STANDARD = [
    ("99 cents", [item("twine", 99)], 99, 0),
    ("exactly $1.00", [item("twine", 100)], 100, 1),
    ("$1.01", [item("twine", 101)], 101, 1),
    ("$1.99", [item("twine", 199)], 199, 1),
    ("exactly $2.00", [item("twine", 200)], 200, 2),
    ("$19.99", [item("rake", 1999)], 1999, 19),
    ("two items at $0.60", [item("labels", 60), item("ties", 60)], 120, 1),
    ("one $0.60 item, quantity 2", [item("labels", 60, 2)], 120, 1),
    ("seven items at $0.49", [item(f"packet{n}", 49) for n in range(7)], 343, 3),
    ("$0.33 + $0.33 + $0.34", [item("a", 33), item("b", 33), item("c", 34)], 100, 1),
    ("$0.33 x 3", [item("pegs", 33, 3)], 99, 0),
    ("$0.34 x 3", [item("pegs", 34, 3)], 102, 1),
    ("five $19.99 items", [item(f"tool{n}", 1999) for n in range(5)], 9995, 99),
    ("$0.99 x 101", [item("seeds", 99, 101)], 9999, 99),
    ("$0.01 x 100", [item("washers", 1, 100)], 100, 1),
    ("$0.01 x 99", [item("washers", 1, 99)], 99, 0),
    ("$2.50 x 4", [item("gloves", 250, 4)], 1000, 10),
    ("$123.45 x 7", [item("ladder", 12345, 7)], 86415, 864),
    ("free item and a $5.05 item", [item("sample", 0, 3), item("trowel", 505)], 505, 5),
    ("mixed quantities", [item("pots", 1250, 3), item("soil", 799, 2), item("stakes", 45, 11)], 3750 + 1598 + 495, 58),
    ("$4,999.99", [item("mower", 499999)], 499999, 4999),
    ("$1,000,000.00 x 1", [item("greenhouse", 100000000)], 100000000, 1000000),
    ("gift card left out of the floor", [item("labels", 60), item("gift_card", 60)], 60, 0),
    ("gift card left out of the sum", [item("rake", 1999), item("gift_card", 10001, 2)], 1999, 19),
]

problems = []
for label, items, eligible, base in STANDARD:
    expect(problems, f"standard, {label}", {"tier": "standard", "items": items}, response(eligible, base, 0))

# The tier never changes eligible_cents or base_points.
TIERED = [
    ("gold", [item("rake", 1999)], response(1999, 19, 9)),  # 28.5 -> 28
    ("silver", [item("rake", 1999)], response(1999, 19, 4)),  # 23.75 -> 23
    ("gold", [item("labels", 60), item("ties", 60)], response(120, 1, 0)),  # 1.5 -> 1
    ("silver", [item("pegs", 34, 3), item("gift_card", 900)], response(102, 1, 0)),  # 1.25 -> 1
    ("gold", [item("ladder", 12345, 7)], response(86415, 864, 432)),  # 1296 exactly
]
for tier, items, want in TIERED:
    expect(problems, f"{tier}, {len(items)} items", {"tier": tier, "items": items}, want)

finish(problems, f"base points ok: {len(STANDARD) + len(TIERED)} orders")
