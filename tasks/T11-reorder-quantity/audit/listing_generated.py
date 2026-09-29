"""X14 (C2): 40 generated requests (seed 50929), each at its own budget and at a budget of 0, list every sku once in request order with consistent costs, totals and budget-independent `wanted`."""

import random

from _cmd import call, finish
from _listing import consistent
from _model import product

rng = random.Random(50929)
problems = []
for n in range(40):
    size = rng.randint(1, 10)
    products = []
    for i in range(size):
        demand, lead = rng.randint(0, 15), rng.randint(0, 12)
        products.append(product(
            f"C2-{n:02d}-{rng.choice('KQWX')}{i}", on_hand=rng.randint(0, 120), on_order=rng.choice([0, rng.randint(0, 40)]),
            daily_demand=demand, lead_time_days=lead, safety_stock=rng.randint(0, 30), pack_size=rng.randint(1, 30),
            unit_cost_cents=rng.randint(1, 700), priority=rng.randint(1, 6)))
    budget = rng.choice([0, rng.randint(0, 2000), rng.randint(0, 40000), rng.randint(0, 10 ** 7)])
    wanted_lists = []
    for b in (budget, 0):
        request = {"budget_cents": b, "products": products}
        status, body = call(request)
        if status != 0:
            problems.append(f"request {n}, budget {b}: expected status 0, got {status}")
            break
        wanted = consistent(f"request {n}, budget {b}", request, body, problems)
        if wanted is None:
            break
        wanted_lists.append(wanted)
    else:
        if wanted_lists[0] != wanted_lists[1]:
            problems.append(f"request {n}: wanted must not depend on the budget, got {wanted_lists[0]} with budget "
                            f"{budget} and {wanted_lists[1]} with 0")

finish(problems, "generated listings ok: 40 requests at 2 budgets each")
