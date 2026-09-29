"""X8 (G3): the money left passes from product to product, even after a product is cut short or gets nothing.

Every product in a request has the same priority and the skus sort in request order, so the funding
order is the request order under any reading of G4, and only G3 decides the result.
"""

from _cmd import call, finish
from _model import by_sku, needing, short


def item(sku, packs, pack_size, unit_cost):
    """A product that wants exactly `packs` packs (none when packs is 0)."""
    return (sku, packs * pack_size if packs else -3, pack_size, unit_cost)


# (label, budget, [(sku, units needed, pack size, unit cost)], expected quantities)
CASES = [
    ("a product that cannot afford one pack does not stop a cheaper one after it", 3000,
     [item("CA-big", 1, 10, 500), item("CA-small", 2, 5, 200)], [0, 10]),
    ("a product cut short passes its remainder on", 2500,
     [item("CB-1", 5, 4, 175), item("CB-2", 1, 2, 200), item("CB-3", 3, 1, 1)], [12, 2, 0]),
    ("a product cut short passes its remainder on, one cent more", 2501,
     [item("CB-1", 5, 4, 175), item("CB-2", 1, 2, 200), item("CB-3", 3, 1, 1)], [12, 2, 1]),
    ("a product that wants nothing costs nothing", 800,
     [item("CC-1", 2, 3, 100), item("CC-2", 0, 7, 50), item("CC-3", 1, 3, 50)], [6, 0, 3]),
    ("a partly funded product then an unaffordable one", 1500,
     [item("CD-1", 1, 4, 100), item("CD-2", 2, 10, 100), item("CD-3", 4, 3, 50)], [4, 10, 0]),
    ("a partly funded product then an affordable one", 1550,
     [item("CD-1", 1, 4, 100), item("CD-2", 2, 10, 100), item("CD-3", 4, 3, 50)], [4, 10, 3]),
    ("several products skipped before one fits", 750,
     [item("CE-1", 1, 1, 900), item("CE-2", 1, 2, 400), item("CE-3", 1, 7, 100), item("CE-4", 3, 1, 100)], [0, 0, 7, 0]),
    ("a later product fits after earlier skips", 850,
     [item("CE-1", 1, 1, 900), item("CE-2", 1, 2, 400), item("CE-3", 1, 7, 100), item("CE-4", 3, 1, 100)], [0, 2, 0, 0]),
    ("only the last product fits", 650,
     [item("CE-1", 1, 1, 900), item("CE-2", 1, 2, 400), item("CE-3", 1, 7, 100), item("CE-4", 3, 1, 100)], [0, 0, 0, 3]),
    ("a budget of exactly the full cost buys everything", 3660,
     [item("CF-1", 3, 5, 60), item("CF-2", 2, 12, 40), item("CF-3", 4, 1, 450)], [15, 24, 4]),
    ("one cent short of the full cost loses only the last pack", 3659,
     [item("CF-1", 3, 5, 60), item("CF-2", 2, 12, 40), item("CF-3", 4, 1, 450)], [15, 24, 3]),
    ("the first product takes everything it can, the rest is too little for the second", 3000,
     [item("CG-1", 10, 2, 140), item("CG-2", 1, 1, 201)], [20, 0]),
    ("the first product is starved and the second takes the budget exactly", 999,
     [item("CH-1", 2, 50, 20), item("CH-2", 9, 1, 111)], [0, 9]),
    ("an empty budget buys nothing anywhere", 0,
     [item("CI-1", 1, 1, 1), item("CI-2", 3, 2, 5)], [0, 0]),
]
problems = []
for label, budget, items, quantities in CASES:
    products = [needing(sku, need, pack_size=pack, unit_cost_cents=cost, priority=4) for sku, need, pack, cost in items]
    assert [p["sku"] for p in products] == sorted(p["sku"] for p in products)
    status, body = call({"budget_cents": budget, "products": products})
    got = by_sku(body, "quantity")
    got = [got.get(p["sku"], 0) for p in products] if got is not None else None
    if status != 0 or got != quantities:
        problems.append(f"{label} (budget {budget}): expected quantities {quantities}, got status {status} and {short(got if got else body, 100)}")

finish(problems, f"carried budgets ok: {len(CASES)} requests")
