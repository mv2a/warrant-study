"""P1: `reorder` follows the interface in C1, and refuses a negative stock on hand (C3)."""

from _cmd import call, finish

TOP = {"orders", "total_cost_cents", "budget_left_cents"}
ORDER = {"sku", "wanted", "quantity", "cost_cents"}


def product(sku, **values):
    base = {"sku": sku, "on_hand": 3, "on_order": 0, "daily_demand": 2, "lead_time_days": 5,
            "safety_stock": 4, "pack_size": 6, "unit_cost_cents": 120, "priority": 1}
    base.update(values)
    return base


REQUESTS = [
    {"budget_cents": 50000, "products": [product("P-100")]},
    {"budget_cents": 2000, "products": [product("P-200", priority=2), product("P-201", on_hand=40)]},
]
problems = []
for request in REQUESTS:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
        continue
    if not isinstance(body, dict) or set(body) != TOP:
        problems.append(f"{request}: expected an object with exactly {sorted(TOP)}, got {body!r}")
        continue
    if type(body["total_cost_cents"]) is not int or type(body["budget_left_cents"]) is not int:
        problems.append(f"{request}: the totals must be whole numbers of cents, got {body!r}")
    orders = body["orders"]
    if not isinstance(orders, list) or len(orders) != len(request["products"]):
        problems.append(f"{request}: expected one order per product, got {orders!r}")
        continue
    if sorted(str(o.get("sku")) for o in orders if isinstance(o, dict)) != sorted(p["sku"] for p in request["products"]):
        problems.append(f"{request}: expected one order for each sku, got {orders!r}")
    for order, sent in zip(orders, request["products"]):
        if not isinstance(order, dict) or set(order) != ORDER:
            problems.append(f"{sent['sku']}: expected an order with exactly {sorted(ORDER)}, got {order!r}")
        elif type(order["sku"]) is not str:
            problems.append(f"{sent['sku']}: sku must be a string, got {order!r}")
        elif not all(type(order[f]) is int for f in ("wanted", "quantity", "cost_cents")):
            problems.append(f"{sent['sku']}: wanted, quantity and cost_cents must be integers, got {order!r}")

status, body = call({"budget_cents": 50000, "products": [product("P-300", on_hand=-1)]})
if status != 2 or body is not None:
    problems.append(f"a negative on_hand must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, f"contract ok: {len(REQUESTS) + 1} requests")
