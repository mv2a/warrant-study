"""The audit's own reading of intent.md: an oracle for the plan, plus builders for requests.

Written from intent.md alone (G1 to G4, C2). Integer arithmetic only.
"""

FIELDS = ("on_hand", "on_order", "daily_demand", "lead_time_days", "safety_stock",
          "pack_size", "unit_cost_cents", "priority")


def product(sku, on_hand=0, on_order=0, daily_demand=0, lead_time_days=0, safety_stock=0,
            pack_size=1, unit_cost_cents=1, priority=1):
    return {"sku": sku, "on_hand": on_hand, "on_order": on_order, "daily_demand": daily_demand,
            "lead_time_days": lead_time_days, "safety_stock": safety_stock, "pack_size": pack_size,
            "unit_cost_cents": unit_cost_cents, "priority": priority}


def needing(sku, needed, pack_size=1, unit_cost_cents=1, priority=1):
    """A product whose units needed (G1) is exactly `needed` (zero or less means nothing).

    The need is a daily demand over a one-day lead time, with no stock and no safety stock,
    so checks of G2, G3 and G4 do not hinge on the finer points of the G1 formula.
    """
    if needed >= 0:
        return product(sku, daily_demand=needed, lead_time_days=1, pack_size=pack_size,
                       unit_cost_cents=unit_cost_cents, priority=priority)
    return product(sku, on_hand=-needed, pack_size=pack_size,
                   unit_cost_cents=unit_cost_cents, priority=priority)


def needed(p):
    """G1: target minus on hand minus on order, never below zero."""
    target = p["daily_demand"] * p["lead_time_days"] + p["safety_stock"]
    return max(0, target - p["on_hand"] - p["on_order"])


def wanted(p):
    """G2: units needed rounded up to the next multiple of the pack size."""
    n = needed(p)
    return -(-n // p["pack_size"]) * p["pack_size"]


def funding_order(products):
    """G4: smaller priority first; equal priorities in request order."""
    return sorted(range(len(products)), key=lambda i: (products[i]["priority"], i))


def plan(request):
    """The full response the intent promises for a valid request."""
    products = request["products"]
    want = [wanted(p) for p in products]
    quantity = [0] * len(products)
    left = request["budget_cents"]
    for i in funding_order(products):
        p = products[i]
        pack_cost = p["pack_size"] * p["unit_cost_cents"]
        packs = min(want[i] // p["pack_size"], left // pack_cost)
        quantity[i] = packs * p["pack_size"]
        left -= packs * pack_cost
    orders = [{"sku": p["sku"], "wanted": want[i], "quantity": quantity[i],
               "cost_cents": quantity[i] * p["unit_cost_cents"]} for i, p in enumerate(products)]
    total = sum(o["cost_cents"] for o in orders)
    return {"orders": orders, "total_cost_cents": total,
            "budget_left_cents": request["budget_cents"] - total}


def by_sku(body, field):
    """{sku: value of `field`} from a response's orders, or None when it has no usable orders list.

    Checks of G1 to G4 match orders to products by sku, so a response listed in the wrong order
    (a C2 matter) is judged on its amounts alone; a product left out counts as wanting and
    ordering nothing.
    """
    if not isinstance(body, dict) or not isinstance(body.get("orders"), list):
        return None
    if not all(isinstance(o, dict) for o in body["orders"]):
        return None
    return {o.get("sku"): o.get(field) for o in body["orders"]}


def short(value, limit=150):
    text = repr(value)
    return text if len(text) <= limit else text[:limit - 3] + "..."
