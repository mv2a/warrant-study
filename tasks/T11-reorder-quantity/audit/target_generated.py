"""X4 (G1): 150 generated products (seed 61903), in packs of one, get exactly the units they need as `wanted`."""

import random

from _cmd import call, finish
from _model import by_sku, needed, product, short

rng = random.Random(61903)


def generated(sku):
    demand = rng.choice([0, 0, 1, 2, 3, rng.randint(4, 40), rng.randint(41, 900)])
    lead = rng.choice([0, 1, rng.randint(2, 14), rng.randint(15, 120)])
    safety = rng.choice([0, rng.randint(1, 30), rng.randint(31, 4000)])
    target = demand * lead + safety
    style = rng.randint(0, 4)  # styles 0 and 1 (about two fifths) put stock on or near the target
    if style == 0:        # stock lands exactly on the target
        on_hand = rng.randint(0, target)
        on_order = target - on_hand
    elif style == 1:      # just below or just above the target
        total = max(0, target + rng.choice([-2, -1, 1, 2]))
        on_hand = rng.randint(0, total)
        on_order = total - on_hand
    else:
        on_hand = rng.randint(0, target + 50)
        on_order = rng.choice([0, 0, rng.randint(0, target + 10)])
    return product(sku, on_hand=on_hand, on_order=on_order, daily_demand=demand, lead_time_days=lead,
                   safety_stock=safety, pack_size=1, unit_cost_cents=rng.randint(1, 9), priority=rng.randint(1, 4))


problems = []
count = 0
for batch in range(6):
    products = [generated(f"G1-{batch}-{i:02d}") for i in range(25)]
    status, body = call({"budget_cents": 10 ** 12, "products": products})
    got = by_sku(body, "wanted")
    if status != 0 or got is None:
        problems.append(f"batch {batch}: expected status 0 and a plan, got status {status} and {short(body)}")
        continue
    for p in products:
        count += 1
        if got.get(p["sku"], 0) != needed(p):
            problems.append(f"{p['sku']} (on hand {p['on_hand']}, on order {p['on_order']}, demand {p['daily_demand']}, "
                            f"lead {p['lead_time_days']}, safety {p['safety_stock']}): needs {needed(p)}, "
                            f"got wanted={got.get(p['sku'], 0)!r}")

finish(problems, f"generated targets ok: {count} products")
