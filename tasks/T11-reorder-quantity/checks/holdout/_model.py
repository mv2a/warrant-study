"""Shared helpers for the hidden checks: request builders and the expected plan, read from intent.md."""

import random

FIELDS = ("on_hand", "on_order", "daily_demand", "lead_time_days", "safety_stock",
          "pack_size", "unit_cost_cents", "priority")


def product(sku, on_hand=0, on_order=0, daily_demand=0, lead_time_days=0, safety_stock=0,
            pack_size=1, unit_cost_cents=1, priority=1):
    return {"sku": sku, "on_hand": on_hand, "on_order": on_order, "daily_demand": daily_demand,
            "lead_time_days": lead_time_days, "safety_stock": safety_stock, "pack_size": pack_size,
            "unit_cost_cents": unit_cost_cents, "priority": priority}


def needed(p):
    """G1: units needed to reach daily demand x lead time + safety stock."""
    target = p["daily_demand"] * p["lead_time_days"] + p["safety_stock"]
    return max(0, target - p["on_hand"] - p["on_order"])


def wanted(p):
    """G2: units needed, rounded up to whole packs."""
    packs, rest = divmod(needed(p), p["pack_size"])
    return (packs + (1 if rest else 0)) * p["pack_size"]


def expected(request):
    """The full response the intent promises for a valid request."""
    products, left = request["products"], request["budget_cents"]
    quantity = {}
    # G4: smaller priority first; ties keep request order.
    for position in sorted(range(len(products)), key=lambda i: (products[i]["priority"], i)):
        p = products[position]
        pack_cost = p["pack_size"] * p["unit_cost_cents"]
        packs = min(wanted(p) // p["pack_size"], left // pack_cost)  # G3
        quantity[position] = packs * p["pack_size"]
        left -= packs * pack_cost
    orders = [{"sku": p["sku"], "wanted": wanted(p), "quantity": quantity[i],
               "cost_cents": quantity[i] * p["unit_cost_cents"]} for i, p in enumerate(products)]
    total = sum(o["cost_cents"] for o in orders)
    return {"orders": orders, "total_cost_cents": total, "budget_left_cents": request["budget_cents"] - total}


def random_product(rng, sku, priorities=(1, 9)):
    daily = rng.choice([0, 1, 2, 3, 5, 8, 12, 20, 45])
    lead = rng.choice([0, 1, 2, 3, 5, 7, 10, 14, 21])
    safety = rng.randint(0, 60)
    target = daily * lead + safety
    on_hand = rng.randint(0, target + 20)
    on_order = rng.choice([0, 0, rng.randint(0, max(1, target))])
    return product(sku, on_hand, on_order, daily, lead, safety,
                   pack_size=rng.choice([1, 2, 4, 5, 6, 10, 12, 24, 25, 50, 100]),
                   unit_cost_cents=rng.choice([1, 7, 35, 99, 150, 249, 400, 1250]),
                   priority=rng.randint(*priorities))


def random_skus(rng, count):
    """Distinct skus in an order that is usually not alphabetical."""
    skus = set()
    while len(skus) < count:
        skus.add(rng.choice("ABCDEFGHKMNPRSTWXZ") + rng.choice("ABCDEFGHKMNPRSTWXZ") + f"-{rng.randint(10, 999)}")
    skus = sorted(skus)
    rng.shuffle(skus)
    return skus


def full_cost(products):
    return sum(wanted(p) * p["unit_cost_cents"] for p in products)


def random_request(rng, count, priorities=(1, 9), budget_share=None):
    """A request whose budget is a random share of the full cost (0 to 110%)."""
    products = [random_product(rng, sku, priorities) for sku in random_skus(rng, count)]
    share = rng.random() * 1.1 if budget_share is None else budget_share
    return {"budget_cents": int(full_cost(products) * share), "products": products}


def rng_for(seed):
    return random.Random(seed)
