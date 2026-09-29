"""H2: the tier multiplies base points only, and the result is rounded down."""

import random

from _cmd import call, finish

PERCENT = {"standard": 100, "silver": 125, "gold": 150}
rng = random.Random(505202)


def tier_bonus(tier, base):
    return base * PERCENT[tier] // 100 - base


cases = []  # (request, expected bonus_points)
# One line per order, so the base is simply its spend in whole dollars.
for tier in PERCENT:
    for base in list(range(0, 26)) + [rng.randint(26, 1000) for _ in range(10)]:
        quantity = rng.choice([1, 1, 2, 3])
        unit = (base * 100 + rng.randint(0, 99)) // quantity
        while unit * quantity // 100 != base:
            unit += 1
        request = {"tier": tier, "items": [{"category": "grocery", "price_cents": unit, "quantity": quantity}]}
        if rng.random() < 0.3:
            request["bonus_categories"] = ["toys"]  # promoted, but not in this order
        cases.append((request, tier_bonus(tier, unit * quantity // 100)))

# A promoted line in whole dollars: its category points must not be multiplied.
for _ in range(24):
    tier = rng.choice(["silver", "gold"])
    grocery = rng.randint(0, 20000)
    garden_dollars = rng.randint(1, 60)
    base = grocery // 100 + garden_dollars
    request = {"tier": tier, "items": [
        {"category": "grocery", "price_cents": grocery, "quantity": 1},
        {"category": "garden", "price_cents": garden_dollars * 100, "quantity": 1},
    ], "bonus_categories": ["garden"]}
    cases.append((request, tier_bonus(tier, base) + 2 * garden_dollars))

problems = []
for request, expected in cases:
    status, body = call(request)
    got = body.get("bonus_points") if isinstance(body, dict) else None
    if status != 0 or got != expected:
        problems.append(f"{request}: expected bonus_points {expected}, got {got!r} (status {status})")

problems = [p if len(p) <= 220 else p[:217] + "..." for p in problems]
finish(problems, f"tier multipliers ok: {len(cases)} orders")
