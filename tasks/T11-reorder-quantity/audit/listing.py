"""X13 (C2): every product is listed once in request order, and wanted, quantity, cost and the totals follow their definitions."""

from _cmd import call, finish
from _listing import consistent
from _model import product

problems = []
REQUESTS = [
    ("priorities in reverse of the request order", {"budget_cents": 1450, "products": [
        product("LS-c", safety_stock=9, pack_size=3, unit_cost_cents=80, priority=30),
        product("LS-b", safety_stock=5, pack_size=5, unit_cost_cents=60, priority=20),
        product("LS-a", safety_stock=4, pack_size=2, unit_cost_cents=110, priority=10)]}),
    ("products that order nothing are still listed", {"budget_cents": 500, "products": [
        product("NO-full", on_hand=30, daily_demand=2, lead_time_days=5, safety_stock=4, pack_size=6, unit_cost_cents=10, priority=1),
        product("NO-dear", safety_stock=1, pack_size=1, unit_cost_cents=501, priority=2),
        product("NO-met", on_hand=3, on_order=7, daily_demand=1, lead_time_days=10, pack_size=4, unit_cost_cents=5, priority=3),
        product("NO-late", daily_demand=1, lead_time_days=2, pack_size=2, unit_cost_cents=100, priority=4),
        product("NO-poor", safety_stock=9, pack_size=3, unit_cost_cents=1000, priority=5)]}),
    ("a budget of zero still reports what is wanted", {"budget_cents": 0, "products": [
        product("ZB-1", on_hand=1, daily_demand=3, lead_time_days=4, safety_stock=2, pack_size=5, unit_cost_cents=40, priority=2),
        product("ZB-2", on_order=4, daily_demand=2, lead_time_days=7, safety_stock=0, pack_size=12, unit_cost_cents=9, priority=1)]}),
    ("twelve mixed products", {"budget_cents": 20000, "products": [
        product(f"MX-{i:02d}", on_hand=(7 * i) % 23, on_order=(3 * i) % 5, daily_demand=i % 6, lead_time_days=2 + i % 4,
                safety_stock=(5 * i) % 11, pack_size=1 + (i * 5) % 9, unit_cost_cents=15 + 37 * i, priority=1 + (i * 7) % 5)
        for i in range(12)]}),
    ("a large budget left over", {"budget_cents": 10 ** 11 + 7, "products": [
        product("LB-1", daily_demand=40, lead_time_days=30, safety_stock=100, pack_size=50, unit_cost_cents=1234, priority=1)]}),
]


for label, request in REQUESTS:
    wanted_lists = []
    for budget in (request["budget_cents"], 0, 10 ** 15):
        variant = dict(request, budget_cents=budget)
        status, body = call(variant)
        if status != 0:
            problems.append(f"{label}, budget {budget}: expected status 0, got {status}")
            break
        wanted = consistent(f"{label}, budget {budget}", variant, body, problems)
        if wanted is None:
            break
        wanted_lists.append(wanted)
    else:
        if not wanted_lists[0] == wanted_lists[1] == wanted_lists[2]:
            problems.append(f"{label}: wanted must not depend on the budget, got {wanted_lists[0]} with budget "
                            f"{request['budget_cents']}, {wanted_lists[1]} with 0 and {wanted_lists[2]} with 10**15")

finish(problems, f"listing ok: {len(REQUESTS)} requests at 3 budgets each")
