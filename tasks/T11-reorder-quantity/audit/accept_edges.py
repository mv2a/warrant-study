"""X19 (C3): requests on the valid side of every refusal rule are planned, not refused: an empty product list, a budget and counts of 0, pack size, unit cost and priority of 1, and distinct non-empty skus."""

from _cmd import call, finish
from _model import short
from _refuse import good_product

problems = []


def expect_planned(name, request):
    status, body = call(request)
    orders = body.get("orders") if isinstance(body, dict) else None
    if status != 0 or not isinstance(orders, list):
        problems.append(f"{name}: a valid request must be planned (status 0 and a plan), got status {status} and {short(body, 80)}")


# An empty product list is valid, and its plan orders nothing.
for budget in (60000, 0):
    status, body = call({"budget_cents": budget, "products": []})
    if status != 0 or not isinstance(body, dict) or body.get("orders") != []:
        problems.append(f"an empty product list with a budget of {budget}: expected status 0 and a plan with no orders, "
                        f"got status {status} and {short(body, 80)}")
expect_planned("a budget of 0", {"budget_cents": 0, "products": [good_product("AE-1"), good_product("AE-2")]})
for field in ("on_hand", "on_order", "daily_demand", "lead_time_days", "safety_stock"):
    expect_planned(f"{field} of 0", {"budget_cents": 60000, "products": [good_product("AE-1"), good_product("AE-2", **{field: 0})]})
expect_planned("every count 0 at once", {"budget_cents": 60000, "products": [good_product(
    "AE-0", on_hand=0, on_order=0, daily_demand=0, lead_time_days=0, safety_stock=0)]})
for field in ("pack_size", "unit_cost_cents", "priority"):
    expect_planned(f"{field} of 1", {"budget_cents": 60000, "products": [good_product("AE-1", **{field: 1}), good_product("AE-2")]})
expect_planned("every minimum at once", {"budget_cents": 0, "products": [good_product(
    "AE-min", on_hand=0, on_order=0, daily_demand=0, lead_time_days=0, safety_stock=0, pack_size=1, unit_cost_cents=1, priority=1)]})
expect_planned("large whole numbers", {"budget_cents": 10 ** 12, "products": [good_product(
    "AE-big", on_hand=10 ** 9, on_order=10 ** 8, daily_demand=10 ** 6, lead_time_days=3650, safety_stock=10 ** 7,
    pack_size=10 ** 4, unit_cost_cents=10 ** 5, priority=10 ** 9)]})
expect_planned("distinct unusual skus", {"budget_cents": 60000, "products": [
    good_product("7"), good_product("0042"), good_product("hex bolt m8"), good_product("Ø-ring № 5"),
    good_product("ab-1"), good_product("AB-1")]})
expect_planned("a single-character sku", {"budget_cents": 60000, "products": [good_product("x")]})

finish(problems, "valid edge requests planned")
