"""X9 (G1, G2, G3, C1, C2, C3): 170 generated valid orders with a fixed seed.

Each answer must equal what the intent promises (the independent model in _expect.py):
eligible spend without gift cards, base points floored once, the tier bonus on base points,
the category bonus floored once before doubling, the 500 cap on the two bonuses, and the
four-integer output shape.
"""

import json
import random

from _cmd import finish
from _expect import expect, expected, short

rng = random.Random(4417093)
CATEGORIES = ["garden", "grocery", "tools", "paint", "lighting", "Garden", "pets", "gift_card",
              "outdoor furniture", "seeds", "GIFT_CARD", " tools", "bbq"]
LISTABLE = CATEGORIES + ["", "gift_card", "garden", "decking"]
CASES = 170


def price():
    kind = rng.random()
    if kind < 0.06:
        return 0
    if kind < 0.35:
        return rng.randint(1, 250)
    if kind < 0.70:
        return rng.randint(100, 6000)
    if kind < 0.90:
        return rng.randint(5000, 60000)
    return rng.randint(50000, 400000)


def quantity():
    return rng.randint(1, 3) if rng.random() < 0.85 else rng.randint(4, 30)


def order():
    request = {"tier": rng.choice(["standard", "silver", "gold"]), "items": []}
    count = 0 if rng.random() < 0.05 else rng.randint(1, 6)
    for _ in range(count):
        item = {"category": rng.choice(CATEGORIES), "price_cents": price(), "quantity": quantity()}
        if rng.random() < 0.1:
            item["sku"] = f"SKU-{rng.randint(1000, 9999)}"
        request["items"].append(item)
    if rng.random() > 0.25:
        promoted = rng.choices(LISTABLE, k=rng.randint(0, 4))
        # Often promote something actually in the order.
        if request["items"] and rng.random() < 0.6:
            promoted.append(rng.choice(request["items"])["category"])
        request["bonus_categories"] = promoted
    if rng.random() < 0.1:
        request["channel"] = rng.choice(["web", "shop", "phone"])
    return request


problems = []
for n in range(CASES):
    request = order()
    expect(problems, f"case {n} {short(json.dumps(request), 110)}", request, expected(request))

finish(problems, f"generated orders ok: {CASES} cases, seed 4417093")
