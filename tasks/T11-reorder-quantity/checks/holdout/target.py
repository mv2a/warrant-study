"""H1 (G1): units needed are daily demand x lead time + safety stock, minus on hand and on order, never below zero."""

from _cmd import call, finish
from _model import needed, product, random_product, random_skus, rng_for

BUDGET = 10**12  # large enough that the budget never matters here
CASES = [
    ("stock on order counts toward the target", product("G1-A", 5, 7, 4, 3, 6)),
    ("stock exactly at the target", product("G1-B", 10, 8, 4, 3, 6)),
    ("one unit short of the target", product("G1-C", 10, 7, 4, 3, 6)),
    ("one unit above the target", product("G1-D", 10, 9, 4, 3, 6)),
    ("far above the target", product("G1-E", 500, 300, 4, 3, 6)),
    ("everything still on order", product("G1-F", 0, 12, 4, 3, 6)),
    ("on order alone exceeds the target", product("G1-G", 0, 30, 4, 3, 6)),
    ("a lead time of zero days", product("G1-H", 4, 0, 50, 0, 9)),
    ("no daily demand", product("G1-I", 2, 3, 0, 14, 9)),
    ("no safety stock", product("G1-J", 11, 4, 6, 5, 0)),
    ("all zero", product("G1-K", 0, 0, 0, 0, 0)),
    ("safety stock alone", product("G1-L", 0, 0, 0, 0, 25)),
    ("large numbers", product("G1-M", 3000, 20000, 1200, 45, 5000)),
    ("on hand alone above the target, nothing on order", product("G1-N", 70, 0, 5, 9, 10)),
]
problems = []
for name, p in CASES:
    status, body = call({"budget_cents": BUDGET, "products": [p]})
    got = body["orders"][0].get("wanted") if status == 0 and isinstance(body, dict) and body.get("orders") else None
    if got != needed(p):
        problems.append(f"{name} ({p}): expected {needed(p)} units wanted with packs of 1, got status {status} and {got!r}")

rng = rng_for(110101)
generated = 0
for _ in range(6):
    products = []
    for sku in random_skus(rng, 10):
        p = random_product(rng, sku)
        p["pack_size"] = 1
        products.append(p)
    generated += len(products)
    status, body = call({"budget_cents": BUDGET, "products": products})
    got = {o.get("sku"): o.get("wanted") for o in body["orders"]} if status == 0 and isinstance(body, dict) and isinstance(body.get("orders"), list) else {}
    for p in products:
        if got.get(p["sku"]) != needed(p):
            problems.append(f"{p}: expected {needed(p)} units wanted with packs of 1, got {got.get(p['sku'])!r}")

finish(problems, f"target ok: {len(CASES)} boundary products and {generated} generated ones")
