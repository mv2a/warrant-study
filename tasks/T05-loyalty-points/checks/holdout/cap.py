"""H5: bonus points are capped at 500 per order; base points never are."""

import random

from _cmd import call, finish

PERCENT = {"standard": 100, "silver": 125, "gold": 150}
CATEGORIES = ["grocery", "garden", "books", "toys", "electronics"]
rng = random.Random(505505)

# Whole-dollar prices, and a base divisible by 4 for silver and gold, so that only the
# cap decides the answer.
FIXED = [
    ("standard", [("electronics", 249)], ["electronics"]),
    ("standard", [("electronics", 250)], ["electronics"]),
    ("standard", [("electronics", 251)], ["electronics"]),
    ("standard", [("electronics", 1000)], ["electronics"]),
    ("gold", [("grocery", 1000)], []),
    ("gold", [("grocery", 1004)], []),
    ("gold", [("grocery", 2000)], []),
    ("silver", [("grocery", 2000)], []),
    ("silver", [("grocery", 2004)], []),
    ("silver", [("grocery", 2400)], []),
    ("gold", [("grocery", 500), ("garden", 100)], ["garden"]),
    ("gold", [("grocery", 400), ("garden", 200)], ["garden"]),
    ("gold", [("grocery", 200), ("garden", 104)], ["garden"]),
    ("silver", [("grocery", 800), ("garden", 200)], ["garden"]),
    ("silver", [("grocery", 92), ("garden", 232)], ["garden"]),
    ("gold", [("garden", 4000)], ["garden"]),
]
cases = list(FIXED)
for _ in range(40):
    tier = rng.choice(list(PERCENT))
    lines = [(rng.choice(CATEGORIES), rng.choice([rng.randint(0, 200), rng.randint(200, 1500)]))
             for _ in range(rng.randint(1, 4))]
    promoted = rng.sample(CATEGORIES, rng.randint(0, 2))
    base = sum(dollars for _, dollars in lines)
    if tier != "standard" and base % 4:
        lines.append(("sundries", 4 - base % 4))  # never promoted
    cases.append((tier, lines, promoted))

problems = []
for tier, lines, promoted in cases:
    request = {"tier": tier, "items": [{"category": c, "price_cents": d * 100, "quantity": 1} for c, d in lines],
               "bonus_categories": promoted}
    base = sum(d for _, d in lines)
    uncapped = base * PERCENT[tier] // 100 - base + 2 * sum(d for c, d in lines if c in promoted)
    bonus = min(500, uncapped)
    expected = (base, bonus, base + bonus)
    status, body = call(request)
    got = tuple(body.get(k) for k in ("base_points", "bonus_points", "total_points")) if isinstance(body, dict) else None
    if status != 0 or got != expected:
        problems.append(f"{request}: expected base, bonus, total {expected} (uncapped bonus {uncapped}), got {got!r} (status {status})")

problems = [p if len(p) <= 220 else p[:217] + "..." for p in problems]
finish(problems, f"bonus cap ok: {len(cases)} orders")
