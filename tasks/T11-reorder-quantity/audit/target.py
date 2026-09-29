"""X3 (G1): units needed are demand times lead time plus safety stock, minus on hand and on order, never below zero.

Every product here comes in packs of one, so the units wanted equal the units needed.
"""

from _cmd import call, finish
from _model import by_sku, product, short

# (sku, on_hand, on_order, daily_demand, lead_time_days, safety_stock, units needed)
CASES = [
    ("T-all-zero", 0, 0, 0, 0, 0, 0),
    ("T-formula", 0, 0, 3, 4, 5, 17),            # 3*4 + 5, not 3*(4+5) or (3+5)*4
    ("T-formula-stock", 6, 2, 3, 4, 5, 9),
    ("T-exactly-met", 11, 6, 3, 4, 5, 0),        # on hand + on order == target
    ("T-one-over", 12, 6, 3, 4, 5, 0),
    ("T-one-short", 10, 6, 3, 4, 5, 1),
    ("T-on-order-only", 0, 17, 3, 4, 5, 0),       # units on order count toward the target
    ("T-on-order-part", 0, 14, 3, 4, 5, 3),
    ("T-far-over", 5000, 900, 3, 4, 5, 0),
    ("T-no-demand", 2, 1, 0, 30, 9, 6),           # target is the safety stock alone
    ("T-no-lead", 1, 0, 25, 0, 4, 3),
    ("T-no-safety", 0, 0, 7, 6, 0, 42),
    ("T-safety-only-met", 9, 0, 0, 12, 9, 0),
    ("T-big", 1234, 567, 97, 45, 321, 97 * 45 + 321 - 1234 - 567),
    ("T-large", 10 ** 6, 3 * 10 ** 5, 25000, 60, 777, 25000 * 60 + 777 - 10 ** 6 - 3 * 10 ** 5),
    ("T-on-hand-only", 40, 0, 2, 20, 1, 1),
]
request = {"budget_cents": 10 ** 12, "products": [
    product(sku, on_hand=h, on_order=o, daily_demand=d, lead_time_days=l, safety_stock=s,
            pack_size=1, unit_cost_cents=1, priority=1 + i) for i, (sku, h, o, d, l, s, _) in enumerate(CASES)]}

problems = []
status, body = call(request)
got = by_sku(body, "wanted")
if status != 0 or got is None:
    finish([f"expected status 0 and a plan, got status {status} and {short(body)}"], "")
for sku, h, o, d, l, s, need in CASES:
    if got.get(sku, 0) != need:
        problems.append(f"{sku} (on hand {h}, on order {o}, demand {d}/day, lead {l} days, safety {s}): "
                        f"needs {need} units, got wanted={got.get(sku, 0)!r}")

# The same arithmetic, one product per request, so no other product can influence it.
for sku, h, o, d, l, s, need in CASES[1:8]:
    status, body = call({"budget_cents": 10 ** 9, "products": [
        product(sku, on_hand=h, on_order=o, daily_demand=d, lead_time_days=l, safety_stock=s)]})
    got = by_sku(body, "wanted")
    if status != 0 or got is None or got.get(sku, 0) != need:
        problems.append(f"{sku} alone: needs {need} units, got status {status} and {short(body, 100)}")

finish(problems, f"target ok: {len(CASES)} products and 7 single-product requests")
