"""H3 (G3): products are funded in priority order with whole packs, never beyond the budget, leftovers going on."""

from _cmd import call, finish
from _model import expected, product, random_product, random_skus, rng_for, full_cost


def item(sku, need, pack, unit, priority):
    return product(sku, safety_stock=need, pack_size=pack, unit_cost_cents=unit, priority=priority)


# Every product here has its own priority, listed from most to least urgent.
CASES = [
    ("a budget that exactly pays for everything", 1100,
     [item("B-1", 30, 10, 20, 1), item("B-2", 5, 5, 100, 2)], [30, 5]),
    ("one cent short of the full order", 599, [item("B-3", 30, 10, 20, 1)], [20]),
    ("less than one pack", 199, [item("B-4", 30, 10, 20, 1)], [0]),
    ("a budget of zero", 0, [item("B-5", 30, 10, 20, 1), item("B-6", 1, 1, 1, 2)], [0, 0]),
    ("money left after a cut goes to a later, cheaper product", 2500,
     [item("B-7", 30, 10, 100, 1), item("B-8", 7, 7, 100, 2), item("B-9", 8, 4, 100, 3)], [20, 0, 4]),
    ("an earlier product gets nothing and a later one gets all it wants", 3000,
     [item("B-10", 1, 50, 100, 1), item("B-11", 20, 10, 100, 2)], [0, 20]),
    ("a product that wants nothing uses no budget", 1000,
     [product("B-12", on_hand=50, safety_stock=10, pack_size=10, unit_cost_cents=100, priority=1),
      item("B-13", 10, 10, 100, 2)], [0, 10]),
    ("single units that nearly use the budget", 1000, [item("B-14", 5, 1, 333, 1)], [3]),
    ("no more than wanted even with money to spare", 100000, [item("B-15", 11, 6, 50, 1)], [12]),
    ("several cuts in a row", 1200,
     [item("B-16", 10, 5, 90, 1), item("B-17", 6, 2, 60, 2), item("B-18", 9, 3, 50, 3), item("B-19", 10, 1, 10, 4)],
     [10, 4, 0, 6]),
]
problems = []


def quantities(request):
    status, body = call(request)
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("orders"), list):
        return None, None
    got = {o.get("sku"): o.get("quantity") for o in body["orders"] if isinstance(o, dict)}
    return [got.get(p["sku"]) for p in request["products"]], body.get("total_cost_cents")


for name, budget, products, want in CASES:
    request = {"budget_cents": budget, "products": products}
    assert [o["quantity"] for o in expected(request)["orders"]] == want, name
    got, total = quantities(request)
    if got != want:
        problems.append(f"{name}: expected quantities {want}, got {got!r}")
    elif not isinstance(total, int) or total > budget:
        problems.append(f"{name}: the total {total!r} is over the budget of {budget}")

rng = rng_for(110303)
for n in range(60):
    count = rng.randint(1, 7)
    products = [random_product(rng, sku) for sku in random_skus(rng, count)]
    for priority, p in zip(sorted(rng.sample(range(1, 40), count)), products):
        p["priority"] = priority
    budget = int(full_cost(products) * rng.random() * 1.1) if n % 10 else rng.randint(0, 3000)
    request = {"budget_cents": budget, "products": products}
    want = [o["quantity"] for o in expected(request)["orders"]]
    got, total = quantities(request)
    if got != want:
        problems.append(f"generated request {n} (budget {budget}): expected quantities {want}, got {got!r}")
    elif not isinstance(total, int) or total > budget:
        problems.append(f"generated request {n}: the total {total!r} is over the budget of {budget}")

finish(problems, f"budget ok: {len(CASES)} designed requests and 60 generated ones")
