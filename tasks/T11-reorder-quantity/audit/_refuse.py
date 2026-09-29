"""Shared by the C3 checks: a valid request to break, and the test that a request is refused."""

import json

from _cmd import call
from _model import short


def good_product(sku, **values):
    base = {"sku": sku, "on_hand": 4, "on_order": 2, "daily_demand": 3, "lead_time_days": 5, "safety_stock": 6,
            "pack_size": 8, "unit_cost_cents": 45, "priority": 2}
    base.update(values)
    return base


def good_request():
    """Valid on its own: three products, any of which a check may spoil."""
    return {"budget_cents": 60000, "products": [good_product("RF-100"), good_product("RF-200", priority=1),
                                                good_product("RF-300", on_hand=0, priority=3)]}


def expect_refusal(name, problems, request=None, raw=None):
    text = raw if raw is not None else json.dumps(request)
    status, body = call(raw=text)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, nothing on stdout), got status {status} and {short(body, 80)}")


def expect_plan(name, problems, request=None, raw=None):
    """The control: the unspoilt request must be planned, or the refusals above prove nothing."""
    text = raw if raw is not None else json.dumps(request)
    status, body = call(raw=text)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{name}: a valid request must be planned with status 0, got status {status} and {short(body, 80)}")
