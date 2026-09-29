"""X9 (G3): 60 generated requests (seed 80537), funded in request order, get exactly the quantities of the greedy pack-by-pack funding, within budget.

Every product in a request has the same priority and the skus sort in request order, so the funding
order is the request order under any reading of G4; each product needs a whole number of packs (or
nothing), so the result hinges on the funding alone.
"""

import random

from _cmd import call, finish
from _model import by_sku, needing, plan, short, wanted

rng = random.Random(80537)


def generated(sku, priority):
    pack = rng.choice([1, 1, 2, rng.randint(3, 12), rng.randint(13, 48)])
    packs = rng.choice([0, 1, 1, 2, 3, rng.randint(4, 9), rng.randint(10, 30)])
    cost = rng.choice([1, rng.randint(2, 60), rng.randint(61, 900)])
    need = packs * pack if packs else -rng.randint(1, 20)
    return needing(sku, need, pack_size=pack, unit_cost_cents=cost, priority=priority)


problems = []
for n in range(60):
    tier = rng.choice([1, 3, 12])
    products = [generated(f"G3-{n:02d}-{i}", tier) for i in range(rng.randint(2, 8))]
    full = sum(wanted(p) * p["unit_cost_cents"] for p in products)
    budget = rng.choice([0, full, max(0, full - 1), full + rng.randint(1, 500),
                         rng.randint(0, max(1, full)), rng.randint(0, max(1, full // 3)),
                         rng.randint(0, max(1, full // 3))])
    request = {"budget_cents": budget, "products": products}
    expected = [o["quantity"] for o in plan(request)["orders"]]
    status, body = call(request)
    got = by_sku(body, "quantity")
    got = [got.get(p["sku"], 0) for p in products] if got is not None else None
    if status != 0 or got != expected:
        problems.append(f"request {n} (budget {budget}, {len(products)} products): expected quantities {expected}, "
                        f"got status {status} and {short(got if got else body, 90)}")
        continue
    spent = sum(q * p["unit_cost_cents"] for q, p in zip(got, products))
    if spent > budget:
        problems.append(f"request {n}: the quantities cost {spent}, more than the budget {budget}")

finish(problems, "generated funding ok: 60 requests")
