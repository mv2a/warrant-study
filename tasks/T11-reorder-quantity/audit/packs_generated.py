"""X6 (G2): 160 generated products (seed 44117) get `wanted` equal to their need rounded up to a whole number of packs."""

import random

from _cmd import call, finish
from _model import by_sku, needed, product, short, wanted

rng = random.Random(44117)


def generated(sku):
    pack = rng.choice([1, 2, 3, rng.randint(4, 12), rng.randint(13, 60), rng.randint(61, 400)])
    style = rng.randint(0, 5)
    k = rng.randint(0, 30)
    if style == 0:
        need = k * pack                       # exact multiple, including zero
    elif style == 1:
        need = k * pack + 1
    elif style == 2:
        need = max(1, k * pack - 1)
    elif style == 3:
        need = -rng.randint(1, 50)            # stock above target
    else:
        need = rng.randint(1, 3000)
    cost, priority = rng.randint(1, 5), rng.randint(1, 3)
    if need > 0:
        # Demand over a lead time that divides the need, with no stock and no safety stock.
        lead = rng.choice([d for d in range(1, 13) if need % d == 0])
        return product(sku, daily_demand=need // lead, lead_time_days=lead, pack_size=pack,
                       unit_cost_cents=cost, priority=priority)
    demand, lead = rng.randint(0, 9), rng.randint(0, 9)
    return product(sku, on_hand=demand * lead - need, daily_demand=demand, lead_time_days=lead, pack_size=pack,
                   unit_cost_cents=cost, priority=priority)


problems = []
count = 0
for batch in range(8):
    products = [generated(f"G2-{batch}-{i:02d}") for i in range(20)]
    status, body = call({"budget_cents": 10 ** 12, "products": products})
    got = by_sku(body, "wanted")
    if status != 0 or got is None:
        problems.append(f"batch {batch}: expected status 0 and a plan, got status {status} and {short(body)}")
        continue
    for p in products:
        count += 1
        if got.get(p["sku"], 0) != wanted(p):
            problems.append(f"{p['sku']}: {needed(p)} needed in packs of {p['pack_size']}, expected wanted={wanted(p)}, "
                            f"got {got.get(p['sku'], 0)!r}")

finish(problems, f"generated packs ok: {count} products")
