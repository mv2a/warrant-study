"""X2 (C1): other fields are ignored, and the request is read as one JSON object whatever its layout."""

import json

from _cmd import call, finish
from _model import product, short

BASE = {"budget_cents": 2600, "products": [
    product("LM-7", on_hand=1, daily_demand=2, lead_time_days=3, safety_stock=4, pack_size=3, unit_cost_cents=110, priority=2),
    product("LM-8", on_order=2, daily_demand=1, lead_time_days=8, safety_stock=0, pack_size=4, unit_cost_cents=95, priority=1),
    product("LM-9", on_hand=50, daily_demand=1, lead_time_days=2, safety_stock=3, pack_size=10, unit_cost_cents=20, priority=3)]}

# Extra fields, some of them holding values that would be refused if they were real fields.
EXTRA_TOP = {"currency": "EUR", "note": None, "budget": -5, "warehouse": {"id": 3, "open": True}, "run": [1, 2.5]}
EXTRA_PRODUCT = [
    {"name": "lock nut", "weight_kg": 0.25, "supplier": None},
    {"discontinued": True, "min_order": -2, "tags": ["m8", "zinc"], "Priority": "high"},
    {"location": {"aisle": 4}, "reorder_point": 1.5, "sku_alias": ""},
]


def with_extras(request):
    extended = dict(request, **EXTRA_TOP)
    extended["products"] = [dict(p, **extra) for p, extra in zip(request["products"], EXTRA_PRODUCT)]
    return extended


problems = []
status, plain = call(BASE)
if status != 0 or not isinstance(plain, dict):
    finish([f"the plain request: expected status 0 and a plan, got status {status} and {short(plain)}"], "")

VARIANTS = [
    ("extra fields at the top and in every product", json.dumps(with_extras(BASE))),
    ("pretty-printed input with keys in reverse order and surrounding blank lines",
     "\n\n  " + json.dumps({k: ([dict(reversed(list(p.items()))) for p in v] if k == "products" else v)
                             for k, v in reversed(list(BASE.items()))}, indent=3) + "\n\n"),
    ("extra fields, sorted keys and tab indentation", "\t" + json.dumps(with_extras(BASE), sort_keys=True, indent="\t")),
]
for name, raw in VARIANTS:
    status, body = call(raw=raw)
    if status != 0 or body != plain:
        problems.append(f"{name}: expected status 0 and the same plan as the plain request {short(plain, 90)}, "
                        f"got status {status} and {short(body, 90)}")

finish(problems, f"ignored fields ok: {len(VARIANTS)} variants give the plain request's plan")
