"""H4: gift cards earn nothing, not even when gift_card is a promoted category."""

import random

from _cmd import call, finish

CATEGORIES = ["grocery", "garden", "books", "toys", "electronics", "clothing", "pets"]
TIERS = ["standard", "silver", "gold"]
ZERO = {"eligible_cents": 0, "base_points": 0, "bonus_points": 0, "total_points": 0}
rng = random.Random(505404)


def gift_card():
    return {"category": "gift_card", "price_cents": rng.choice([2500, 5000, 10000, rng.randint(1, 60000)]),
            "quantity": rng.randint(1, 4)}


problems = []
checked = 0

# Orders of only gift cards earn nothing at all.
for tier in TIERS:
    for promoted in (None, [], ["gift_card"], ["garden", "gift_card"]):
        request = {"tier": tier, "items": [gift_card() for _ in range(rng.randint(1, 3))]}
        if promoted is not None:
            request["bonus_categories"] = promoted
        status, body = call(request)
        checked += 1
        if status != 0 or body != ZERO:
            problems.append(f"{request}: expected {ZERO}, got {body!r} (status {status})")

# Adding gift cards to any order changes nothing in the response.
for _ in range(40):
    tier = rng.choice(TIERS)
    items = [
        {"category": rng.choice(CATEGORIES), "price_cents": rng.randint(0, 30000), "quantity": rng.randint(1, 3)}
        for _ in range(rng.randint(0, 4))
    ]
    promoted = rng.sample(CATEGORIES, rng.randint(0, 2))
    if rng.random() < 0.6:
        promoted.insert(rng.randint(0, len(promoted)), "gift_card")
    with_cards = list(items)
    for _ in range(rng.randint(1, 3)):
        with_cards.insert(rng.randint(0, len(with_cards)), gift_card())
    plain = {"tier": tier, "items": items, "bonus_categories": promoted}
    mixed = {"tier": tier, "items": with_cards, "bonus_categories": promoted}
    status_plain, expected = call(plain)
    status_mixed, got = call(mixed)
    checked += 1
    if status_plain != 0 or status_mixed != 0 or got != expected:
        problems.append(f"{mixed}: gift cards changed the result from {expected!r} to {got!r} "
                        f"(status {status_plain}, {status_mixed})")

# Absolute values for two mixed orders.
for request, expected in [
    ({"tier": "standard", "items": [{"category": "gift_card", "price_cents": 10000, "quantity": 1},
                                    {"category": "toys", "price_cents": 1220, "quantity": 1}],
      "bonus_categories": ["gift_card", "toys"]},
     {"eligible_cents": 1220, "base_points": 12, "bonus_points": 24, "total_points": 36}),
    ({"tier": "gold", "items": [{"category": "books", "price_cents": 1099, "quantity": 1},
                                {"category": "gift_card", "price_cents": 5001, "quantity": 2}],
      "bonus_categories": ["gift_card"]},
     {"eligible_cents": 1099, "base_points": 10, "bonus_points": 5, "total_points": 15}),
]:
    status, body = call(request)
    checked += 1
    if status != 0 or body != expected:
        problems.append(f"{request}: expected {expected}, got {body!r} (status {status})")

# Only the exact string "gift_card" is a gift card: spacing or case variants are ordinary items.
for look_alike in ("  gift_card  ", "gift_card\t", "\ngift_card", "Gift_card"):
    request = {"tier": "silver", "items": [{"category": look_alike, "price_cents": 4000, "quantity": 1}],
               "bonus_categories": [look_alike]}
    # silver: $40.00 -> base 40, tier 10, promoted 80.
    expected = {"eligible_cents": 4000, "base_points": 40, "bonus_points": 90, "total_points": 130}
    status, body = call(request)
    checked += 1
    if status != 0 or body != expected:
        problems.append(f"{request}: expected {expected}, got {body!r} (status {status})")

problems = [p if len(p) <= 220 else p[:217] + "..." for p in problems]
finish(problems, f"gift cards ok: {checked} comparisons")
