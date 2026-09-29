"""H1: one base point per whole dollar of eligible spend, counted on the order total."""

import random

from _cmd import call, finish

CATEGORIES = ["grocery", "garden", "books", "toys", "electronics", "clothing", "pets"]
TIERS = ["standard", "silver", "gold"]
rng = random.Random(505101)


def order(lines, tier="standard", promoted=None):
    request = {"tier": tier, "items": [
        {"category": category, "price_cents": price, "quantity": quantity}
        for category, price, quantity in lines
    ]}
    if promoted is not None:
        request["bonus_categories"] = promoted
    return request


FIXED = [
    [],
    [("books", 0, 5)],
    [("books", 99, 1)],
    [("books", 100, 1)],
    [("books", 101, 1)],
    [("toys", 60, 1), ("toys", 60, 1)],
    [("toys", 60, 2)],
    [("grocery", 34, 3)],
    [("grocery", 33, 1), ("garden", 33, 1), ("books", 34, 1)],
    [("books", 1999, 1)],
    [("books", 1999, 1), ("toys", 60, 2)],
    [("pets", 50, 7)],
    [("pets", 99, 101)],
    [("electronics", 149999, 3)],
    [("clothing", 1, 1)] * 99,
    [("clothing", 1, 1)] * 100,
]
cases = [order(lines, tier=rng.choice(TIERS)) for lines in FIXED]
for _ in range(60):
    lines = []
    for _ in range(rng.randint(1, 6)):
        price = rng.choice([rng.randint(0, 99), rng.randint(100, 5000), rng.randint(5000, 80000)])
        lines.append((rng.choice(CATEGORIES), price, rng.randint(1, 5)))
    promoted = rng.sample(CATEGORIES, rng.randint(0, 3)) if rng.random() < 0.7 else None
    cases.append(order(lines, tier=rng.choice(TIERS), promoted=promoted))

problems = []
for request in cases:
    spend = sum(item["price_cents"] * item["quantity"] for item in request["items"])
    status, body = call(request)
    got = (body.get("eligible_cents"), body.get("base_points")) if isinstance(body, dict) else None
    if status != 0 or got != (spend, spend // 100):
        problems.append(f"{request}: expected eligible_cents {spend} and base_points {spend // 100}, got {got!r} (status {status})")

problems = [p if len(p) <= 220 else p[:217] + "..." for p in problems]
finish(problems, f"base points ok: {len(cases)} orders")
