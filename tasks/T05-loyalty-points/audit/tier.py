"""X4 (G2): the tier bonus is floor(base points x multiplier) minus base points.

The multiplier works on whole base points (not on cents), rounds down (not to nearest),
and never touches the category bonus. Bonuses here stay under the C2 cap.
"""

from _cmd import finish
from _expect import expect, response

problems = []
count = 0


def order(tier, cents, promoted_cents=0):
    items = [{"category": "benches", "price_cents": cents, "quantity": 1}]
    request = {"tier": tier, "items": items}
    if promoted_cents:
        items.append({"category": "trellis", "price_cents": promoted_cents, "quantity": 1})
        request["bonus_categories"] = ["trellis"]
    return request


def check(label, request, want):
    global count
    count += 1
    expect(problems, label, request, want)


# Worked by hand from G2. Each price carries 99 cents so a multiplier applied to cents
# instead of whole points would give a different answer.
TABLE = [
    # tier, base points, tier bonus
    ("silver", 7, 1),   # 8.75 -> 8 (the intent's example)
    ("silver", 3, 0),   # 3.75 -> 3
    ("silver", 4, 1),   # 5
    ("silver", 5, 1),   # 6.25 -> 6
    ("silver", 6, 1),   # 7.5 -> 7
    ("silver", 8, 2),   # 10
    ("silver", 11, 2),  # 13.75 -> 13
    ("silver", 19, 4),  # 23.75 -> 23
    ("silver", 399, 99),  # 498.75 -> 498
    ("gold", 1, 0),     # 1.5 -> 1
    ("gold", 2, 1),     # 3
    ("gold", 3, 1),     # 4.5 -> 4
    ("gold", 51, 25),   # 76.5 -> 76
    ("gold", 99, 49),   # 148.5 -> 148
    ("gold", 333, 166),  # 499.5 -> 499
    ("standard", 7, 0),
    ("standard", 99, 0),
    ("standard", 999, 0),
]
for tier, base, bonus in TABLE:
    cents = base * 100 + 99
    check(f"{tier}, base {base}", order(tier, cents), response(cents, base, bonus))

# Every base from 0 to 32 in silver and gold, with the fraction of a dollar varying.
# floor(b x 5/4) - b and floor(b x 3/2) - b in exact integer arithmetic.
for base in range(33):
    cents = base * 100 + (base * 37) % 100
    for tier, bonus in (("silver", base * 5 // 4 - base), ("gold", base * 3 // 2 - base)):
        check(f"{tier}, base {base} from {cents} cents", order(tier, cents), response(cents, base, bonus))

# The multiplier applies to base points only, never to the category bonus.
# silver: base 10, tier 12.5 -> 12 -> 2, category $6.00 -> 12; total bonus 14.
check("silver, multiplier not on category bonus", order("silver", 400, 600), response(1000, 10, 14))
# gold: base 10, tier 15 -> 5, category $10.00 -> 20; total bonus 25.
check("gold, all spend promoted", {"tier": "gold", "items": [{"category": "trellis", "price_cents": 1000, "quantity": 1}], "bonus_categories": ["trellis"]}, response(1000, 10, 25))
# gold: base 7 (from $7.99), tier 10.5 -> 10 -> 3, category $3.50 -> 6; total bonus 9.
check("gold, part promoted", order("gold", 449, 350), response(799, 7, 9))
# silver: base 41, tier 51.25 -> 51 -> 10, category $41.99 -> 82; total 92.
check("silver, all promoted", {"tier": "silver", "items": [{"category": "trellis", "price_cents": 4199, "quantity": 1}], "bonus_categories": ["trellis"]}, response(4199, 41, 92))
# standard: a category bonus stays exactly doubled, never multiplied.
check("standard, promoted", order("standard", 100, 1500), response(1600, 16, 30))

finish(problems, f"tier bonus ok: {count} orders")
