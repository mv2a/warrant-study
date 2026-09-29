"""H3: promoted categories earn 2 points per whole dollar of their combined spend."""

import random

from _cmd import call, finish

CATEGORIES = ["grocery", "garden", "books", "toys", "electronics", "clothing", "pets"]
rng = random.Random(505303)


def order(lines, promoted, tier="standard"):
    request = {"tier": tier, "items": [
        {"category": category, "price_cents": price, "quantity": quantity}
        for category, price, quantity in lines
    ]}
    if promoted is not None:
        request["bonus_categories"] = promoted
    return request


# Standard tier: bonus_points is exactly the category bonus while it stays under the cap.
FIXED = [
    ([("garden", 1099, 1)], ["garden"], 20),
    ([("garden", 1050, 1)], ["garden"], 20),
    ([("garden", 199, 1)], ["garden"], 2),
    ([("garden", 99, 1)], ["garden"], 0),
    ([("garden", 60, 1), ("garden", 60, 1)], ["garden"], 2),
    ([("garden", 333, 3), ("toys", 1, 1)], ["garden", "toys"], 20),
    ([("garden", 500, 1), ("books", 500, 1)], ["garden"], 10),
    ([("garden", 500, 1), ("books", 500, 1)], ["garden", "books"], 20),
    ([("garden", 1000, 1)], ["garden", "garden"], 20),
    ([("garden", 1000, 1)], ["Garden"], 0),
    ([("garden", 1000, 1)], [" garden"], 0),
    ([("garden ", 1000, 1)], ["garden"], 0),
    ([("garden\t", 1000, 1), ("garden", 300, 1)], ["garden\t"], 20),
    ([("garden", 1000, 1)], ["toys"], 0),
    ([("garden", 1000, 1)], [], 0),
    ([("garden", 1000, 1)], None, 0),
    ([("garden", 0, 4)], ["garden"], 0),
    ([("garden", 2499, 10)], ["garden"], 498),
]
cases = [(order(lines, promoted), expected) for lines, promoted, expected in FIXED]

generated = 0
while generated < 50:
    lines = [
        (rng.choice(CATEGORIES), rng.choice([rng.randint(0, 150), rng.randint(150, 6000)]), rng.randint(1, 3))
        for _ in range(rng.randint(1, 6))
    ]
    promoted = rng.sample(CATEGORIES, rng.randint(1, 3))
    if rng.random() < 0.2:
        promoted.append(promoted[0])
    spend = sum(price * quantity for category, price, quantity in lines if category in promoted)
    if spend >= 25000:
        continue  # stay under the bonus cap
    cases.append((order(lines, promoted), 2 * (spend // 100)))
    generated += 1

# Silver and gold: whole-dollar prices and a base divisible by 4 keep the tier bonus exact.
for tier, garden, books, expected in [
    ("silver", 40, 20, 15 + 80),
    ("gold", 40, 20, 30 + 80),
    ("silver", 3, 1, 1 + 6),
    ("gold", 100, 0, 50 + 200),
]:
    request = order([("garden", garden * 100, 1), ("books", books * 100, 1)], ["garden"], tier=tier)
    cases.append((request, expected))

problems = []
for request, expected in cases:
    status, body = call(request)
    got = body.get("bonus_points") if isinstance(body, dict) else None
    if status != 0 or got != expected:
        problems.append(f"{request}: expected bonus_points {expected}, got {got!r} (status {status})")

problems = [p if len(p) <= 220 else p[:217] + "..." for p in problems]
finish(problems, f"category bonus ok: {len(cases)} orders")
