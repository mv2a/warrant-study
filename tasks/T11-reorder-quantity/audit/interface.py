"""X1 (C1): the response shape, exit statuses, and the form of a refusal."""

from _cmd import call, finish
from _model import product, short

TOP = {"orders", "total_cost_cents", "budget_left_cents"}
ORDER = {"sku", "wanted", "quantity", "cost_cents"}

VALID = [
    {"budget_cents": 12345, "products": [
        product("QX-01", on_hand=2, daily_demand=3, lead_time_days=4, safety_stock=5, pack_size=4, unit_cost_cents=75, priority=2),
        product("QX-02", on_hand=90, on_order=10, daily_demand=1, lead_time_days=9, safety_stock=1, pack_size=3, unit_cost_cents=410, priority=1),
        product("QX-03", daily_demand=6, lead_time_days=2, pack_size=5, unit_cost_cents=999, priority=7)]},
    {"budget_cents": 0, "products": [product("valve Ø-12 / brass", safety_stock=7, pack_size=2, unit_cost_cents=50)]},
    {"budget_cents": 987654321, "products": [product("R-%d" % i, on_order=i, daily_demand=i + 1, lead_time_days=3,
                                                      safety_stock=2 * i, pack_size=i + 2, unit_cost_cents=13 * i + 1,
                                                      priority=5 - i % 3) for i in range(6)]},
]
problems = []
for request in VALID:
    status, body = call(request)
    label = "request with skus " + ", ".join(p["sku"] for p in request["products"])
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
        continue
    if not isinstance(body, dict) or set(body) != TOP:
        problems.append(f"{label}: expected one object with exactly {sorted(TOP)}, got {short(body)}")
        continue
    for field in ("total_cost_cents", "budget_left_cents"):
        if type(body[field]) is not int:
            problems.append(f"{label}: {field} must be a JSON integer, got {body[field]!r}")
    orders = body["orders"]
    if not isinstance(orders, list):
        problems.append(f"{label}: orders must be a list, got {short(orders)}")
        continue
    sent = {p["sku"] for p in request["products"]}
    for order in orders:
        if not isinstance(order, dict) or set(order) != ORDER:
            problems.append(f"{label}: expected each order to have exactly {sorted(ORDER)}, got {short(order)}")
            continue
        if type(order["sku"]) is not str or order["sku"] not in sent:
            problems.append(f"{label}: an order's sku must be one of the request's strings, got {order['sku']!r}")
        for field in ("wanted", "quantity", "cost_cents"):
            if type(order[field]) is not int:
                problems.append(f"{label}: {field} must be a JSON integer, got {order[field]!r}")

REFUSED = [
    ("text that is not JSON", "reorder everything please"),
    ("a request without products", '{"budget_cents": 500}'),
    ("a JSON list instead of an object", '[500, []]'),
]
for name, raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: a refusal must exit 2 and write nothing on stdout, got status {status} and {short(body)}")

finish(problems, f"interface ok: {len(VALID)} plans, {len(REFUSED)} refusals")
