"""H6 (C2): every product is listed once in request order, and the amounts add up."""

from _cmd import call, finish
from _model import full_cost, product, random_request, rng_for

problems = []


def check(name, request, big_budget_body=None):
    status, body = call(request)
    if status != 0 or not isinstance(body, dict) or not isinstance(body.get("orders"), list):
        problems.append(f"{name}: expected a plan, got status {status} and {body!r}")
        return None
    orders = body["orders"]
    skus = [o.get("sku") if isinstance(o, dict) else None for o in orders]
    if skus != [p["sku"] for p in request["products"]]:
        problems.append(f"{name}: expected the products in request order {[p['sku'] for p in request['products']]}, got {skus}")
        return None
    for o, p in zip(orders, request["products"]):
        q, w, c = o.get("quantity"), o.get("wanted"), o.get("cost_cents")
        if not all(type(v) is int for v in (q, w, c)):
            problems.append(f"{name} {p['sku']}: expected whole numbers, got {o}")
        elif q % p["pack_size"] or not 0 <= q <= w:
            problems.append(f"{name} {p['sku']}: quantity {q} must be whole packs of {p['pack_size']} between 0 and wanted {w}")
        elif c != q * p["unit_cost_cents"]:
            problems.append(f"{name} {p['sku']}: cost_cents {c} should be {q} x {p['unit_cost_cents']}")
    costs = [o.get("cost_cents") for o in orders]
    if all(type(c) is int for c in costs):
        if body.get("total_cost_cents") != sum(costs):
            problems.append(f"{name}: total_cost_cents {body.get('total_cost_cents')!r} should be the sum of the costs, {sum(costs)}")
        elif body.get("budget_left_cents") != request["budget_cents"] - sum(costs):
            problems.append(f"{name}: budget_left_cents {body.get('budget_left_cents')!r} should be {request['budget_cents']} - {sum(costs)}")
    return body


designed = [
    ("the most urgent product listed last", {"budget_cents": 1500, "products": [
        product("L-1", 0, 0, 2, 5, 0, 5, 100, 3), product("L-2", 0, 0, 1, 5, 0, 5, 100, 2),
        product("L-3", 0, 0, 3, 5, 0, 5, 100, 1)]}),
    ("nothing ordered at all", {"budget_cents": 0, "products": [
        product("L-4", 40, 0, 1, 5, 5, 6, 10, 2), product("L-5", 0, 0, 4, 4, 4, 6, 10, 1)]}),
    ("products that need nothing between others", {"budget_cents": 100000, "products": [
        product("L-6", 0, 0, 2, 2, 2, 4, 30, 9), product("L-7", 99, 0, 1, 1, 1, 4, 30, 1),
        product("L-8", 1, 1, 3, 3, 3, 4, 30, 5), product("L-9", 0, 50, 1, 1, 1, 4, 30, 2)]}),
]
for name, request in designed:
    check(name, request)

rng = rng_for(110606)
for n in range(50):
    request = random_request(rng, rng.randint(1, 8))
    body = check(f"generated request {n}", request)
    # `wanted` is fixed before the budget is applied, so a bigger budget does not change it.
    if body is not None and n % 3 == 0:
        rich = dict(request, budget_cents=full_cost(request["products"]) + 1)
        status, again = call(rich)
        before = [o.get("wanted") for o in body["orders"]]
        after = [o.get("wanted") for o in again["orders"]] if status == 0 and isinstance(again, dict) and isinstance(again.get("orders"), list) else None
        if before != after:
            problems.append(f"generated request {n}: wanted changed with the budget, {before} versus {after}")

finish(problems, f"listing ok: {len(designed)} designed requests and 50 generated ones")
