"""H4 (G4): priority 1 is funded first, larger numbers later, and ties are funded in request order."""

from _cmd import call, finish
from _model import expected, product, random_product, random_skus, rng_for, full_cost


def item(sku, priority, packs=1):
    # One pack costs 1000 cents; the product wants `packs` packs.
    return product(sku, safety_stock=10 * packs, pack_size=10, unit_cost_cents=100, priority=priority)


CASES = [
    ("priority 1 listed last is funded first", 1000, [item("A-1", 2), item("B-1", 1)]),
    ("priority numbers far apart", 2000, [item("A-2", 10), item("B-2", 5), item("C-2", 1)]),
    ("a tie is funded in request order, not by sku", 1000, [item("ZED-3", 1), item("ALF-3", 1)]),
    ("a tie split by a more urgent product", 2000, [item("Z-4", 2), item("A-4", 1), item("B-4", 2)]),
    ("a large priority number is the least urgent", 1000, [item("A-5", 100), item("B-5", 2)]),
    ("a three-way tie", 2000, [item("C-6", 1), item("B-6", 1), item("A-6", 1)]),
    ("an urgent product wanting two packs uses the budget first", 2000,
     [item("A-7", 3), item("B-7", 2, packs=2), item("C-7", 1)]),
    ("ties at a lower priority after a cut", 4000,
     [item("M-8", 7), item("K-8", 3, packs=2), item("D-8", 7), item("Q-8", 3)]),
]
problems = []


def check(name, request):
    want = {o["sku"]: o["quantity"] for o in expected(request)["orders"]}
    status, body = call(request)
    got = ({o.get("sku"): o.get("quantity") for o in body["orders"] if isinstance(o, dict)}
           if status == 0 and isinstance(body, dict) and isinstance(body.get("orders"), list) else None)
    if got != want:
        problems.append(f"{name}: expected quantities {want}, got {got!r}")


for name, budget, products in CASES:
    check(name, {"budget_cents": budget, "products": products})

rng = rng_for(110404)
for n in range(50):
    count = rng.randint(2, 8)
    products = [random_product(rng, sku, priorities=(1, 3)) for sku in random_skus(rng, count)]
    check(f"generated request {n}", {"budget_cents": int(full_cost(products) * rng.uniform(0.15, 0.9)), "products": products})

finish(problems, f"priority ok: {len(CASES)} designed requests and 50 generated ones")
