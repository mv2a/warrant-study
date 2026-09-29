"""H5 (C1): the command's input, output fields and types, and exit statuses follow the interface."""

import json

from _cmd import call, finish
from _model import expected, product, random_request, rng_for

TOP = {"orders", "total_cost_cents", "budget_left_cents"}
ORDER = {"sku", "wanted", "quantity", "cost_cents"}
problems = []


def shape_problem(body, request):
    if not isinstance(body, dict) or set(body) != TOP:
        return f"expected one object with exactly {sorted(TOP)}, got {body!r}"
    if type(body["total_cost_cents"]) is not int or type(body["budget_left_cents"]) is not int:
        return f"total_cost_cents and budget_left_cents must be integers, got {body!r}"
    orders = body["orders"]
    if not isinstance(orders, list) or len(orders) != len(request["products"]):
        return f"expected a list of {len(request['products'])} orders, got {orders!r}"
    for order in orders:
        if not isinstance(order, dict) or set(order) != ORDER:
            return f"expected each order to have exactly {sorted(ORDER)}, got {order!r}"
        if type(order["sku"]) is not str:
            return f"sku must be a string, got {order!r}"
        if not all(type(order[f]) is int for f in ("wanted", "quantity", "cost_cents")):
            return f"wanted, quantity and cost_cents must be integers (not decimals or true/false), got {order!r}"
    return None


rng = rng_for(110505)
valid = [
    ("one product", {"budget_cents": 5000, "products": [product("I-1", 3, 2, 4, 5, 6, 12, 35, 1)]}),
    ("no products", {"budget_cents": 777, "products": []}),
    ("a zero budget", {"budget_cents": 0, "products": [product("I-2", 0, 0, 2, 2, 2, 3, 10, 4)]}),
] + [(f"generated request {n}", random_request(rng, rng.randint(1, 6))) for n in range(12)]
for name, request in valid:
    status, body = call(request)
    if status != 0:
        problems.append(f"{name}: exited with status {status}, expected 0")
        continue
    problem = shape_problem(body, request)
    if problem:
        problems.append(f"{name}: {problem}")

status, body = call({"budget_cents": 777, "products": []})
if status != 0 or body != {"orders": [], "total_cost_cents": 0, "budget_left_cents": 777}:
    problems.append(f"no products: expected an empty plan that keeps the whole budget, got status {status} and {body!r}")

# Fields the interface does not name are ignored.
plain = {"budget_cents": 4000, "products": [product("I-3", 1, 0, 3, 4, 2, 5, 90, 1), product("I-4", 0, 0, 1, 7, 0, 2, 300, 2)]}
extra = {"budget_cents": 4000, "note": "evening run", "warehouse": 3,
         "products": [dict(p, supplier="Acme", colour="red", discontinued=False) for p in plain["products"]]}
status, body = call(extra)
if status != 0 or body != expected(plain):
    problems.append(f"extra fields must be ignored: expected {expected(plain)}, got status {status} and {body!r}")

# The request may be spread over several lines and indented.
status, body = call(raw='{\n  "budget_cents": 4000,\n  "products": [\n    ' + ",\n    ".join(
    json.dumps(p) for p in plain["products"]) + "\n  ]\n}\n")
if status != 0 or body != expected(plain):
    problems.append(f"an indented request over several lines: expected {expected(plain)}, got status {status} and {body!r}")

# A refusal exits with status 2 and writes nothing on standard output.
refusals = [
    ("text that isn't JSON", None, "please reorder"),
    ("a negative budget", {"budget_cents": -5, "products": []}, None),
    ("a missing product list", {"budget_cents": 100}, None),
    ("a pack size of zero", {"budget_cents": 100, "products": [product("I-5", pack_size=0)]}, None),
    ("a repeated sku", {"budget_cents": 100, "products": [product("I-6"), product("I-6")]}, None),
]
for name, request, raw in refusals:
    status, body = call(request, raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: a refusal must exit with status 2 and write nothing on standard output, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(valid) + 3} valid requests and {len(refusals)} refusals")
