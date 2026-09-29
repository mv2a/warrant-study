"""Shared by the G4 checks: reveal the funding order with products that each want exactly one pack.

With a budget equal to the pack prices of the first k products in the expected funding order,
exactly those k products get their pack and nothing is left for the rest. The set of funded
products then shows the order, and it does not depend on how a partly affordable product would
be handled, because no product is ever partly affordable at those budgets.
"""

from _cmd import call
from _model import by_sku, short

PACK_SIZES = [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45, 60, 72, 90, 120, 180, 360]


def one_pack(sku, priority, pack_size=4, price=360):
    """A product that needs exactly one pack of `pack_size` units, priced `price` cents (a multiple of pack_size)."""
    assert price % pack_size == 0
    return {"sku": sku, "on_hand": 0, "on_order": 0, "daily_demand": 1, "lead_time_days": pack_size,
            "safety_stock": 0, "pack_size": pack_size, "unit_cost_cents": price // pack_size,
            "priority": priority}


def price(p):
    return p["pack_size"] * p["unit_cost_cents"]


def funded(products, budget):
    """Call with this budget; return (problem or None, list of funded skus in request order)."""
    status, body = call({"budget_cents": budget, "products": products})
    got = by_sku(body, "quantity")
    if status != 0 or got is None:
        return f"expected status 0 and a plan, got status {status} and {short(body, 100)}", None
    skus = []
    for p in products:
        q = got.get(p["sku"], 0)
        if q == p["pack_size"]:
            skus.append(p["sku"])
        elif q != 0:
            return f"{p['sku']} wants one pack of {p['pack_size']}, got quantity {q!r}", None
    return None, skus


def expected_order(products):
    return [products[i]["sku"] for i in sorted(range(len(products)), key=lambda i: (products[i]["priority"], i))]


def check_order(label, products, problems, ks=None):
    """For each k, a budget paying exactly for the first k products in funding order must fund exactly those."""
    order = expected_order(products)
    prices = {p["sku"]: price(p) for p in products}
    for k in (range(len(order) + 1) if ks is None else ks):
        budget = sum(prices[sku] for sku in order[:k])
        problem, got = funded(products, budget)
        if problem:
            problems.append(f"{label}, budget {budget} (first {k} in funding order): {problem}")
            return
        want = [p["sku"] for p in products if p["sku"] in order[:k]]
        if got != want:
            problems.append(f"{label}, budget {budget}: expected {want or 'nothing'} funded "
                            f"(funding order {order}), got {got or 'nothing'}")
            return
