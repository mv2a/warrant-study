"""X20-X22 (S1, S2, S3): each scenario in the intent, written out in several JSON layouts, gets exactly the stated response.

Usage: python3 scenario.py S1|S2|S3
"""

import json
import random
import sys

from _cmd import call, finish


def product(sku, on_hand, on_order, daily_demand, lead_time_days, safety_stock, pack_size, unit_cost_cents, priority):
    return {"sku": sku, "on_hand": on_hand, "on_order": on_order, "daily_demand": daily_demand,
            "lead_time_days": lead_time_days, "safety_stock": safety_stock, "pack_size": pack_size,
            "unit_cost_cents": unit_cost_cents, "priority": priority}


# Transcribed from intent.md. The responses are the intent's JSON, verbatim.
SCENARIOS = {
    "S1": ({"budget_cents": 100000, "products": [product("BOLT-M6", 20, 12, 8, 5, 15, 24, 35, 1)]},
           '{"orders": [{"sku": "BOLT-M6", "wanted": 24, "quantity": 24, "cost_cents": 840}], '
           '"total_cost_cents": 840, "budget_left_cents": 99160}'),
    "S2": ({"budget_cents": 3500, "products": [product("OF-220", 4, 0, 2, 7, 6, 10, 150, 2),
                                               product("GK-110", 10, 5, 3, 6, 8, 6, 100, 1),
                                               product("HS-300", 0, 0, 1, 10, 2, 5, 400, 3)]},
           '{"orders": [{"sku": "OF-220", "wanted": 20, "quantity": 10, "cost_cents": 1500}, '
           '{"sku": "GK-110", "wanted": 12, "quantity": 12, "cost_cents": 1200}, '
           '{"sku": "HS-300", "wanted": 15, "quantity": 0, "cost_cents": 0}], '
           '"total_cost_cents": 2700, "budget_left_cents": 800}'),
    "S3": ({"budget_cents": 0, "products": [product("WS-40", 30, 10, 5, 4, 20, 12, 90, 1),
                                            product("WS-41", 0, 0, 1, 3, 0, 4, 250, 2)]},
           '{"orders": [{"sku": "WS-40", "wanted": 0, "quantity": 0, "cost_cents": 0}, '
           '{"sku": "WS-41", "wanted": 4, "quantity": 0, "cost_cents": 0}], '
           '"total_cost_cents": 0, "budget_left_cents": 0}'),
}

name = sys.argv[1]
request, response = SCENARIOS[name]
expected = json.loads(response)
rng = random.Random({"S1": 7741, "S2": 7742, "S3": 7743}[name])


def shuffled(value):
    """The same JSON value with the keys of every object in a random order."""
    if isinstance(value, dict):
        keys = list(value)
        rng.shuffle(keys)
        return {k: shuffled(value[k]) for k in keys}
    if isinstance(value, list):
        return [shuffled(v) for v in value]
    return value


LAYOUTS = [
    ("compact", json.dumps(request, separators=(",", ":"))),
    ("indented with CRLF line ends", json.dumps(request, indent=4).replace("\n", "\r\n") + "\r\n"),
    ("keys shuffled", json.dumps(shuffled(request))),
    ("keys sorted, one line, padded", "   " + json.dumps(request, sort_keys=True) + "   \n"),
]
problems = []
for layout, text in LAYOUTS:
    status, body = call(raw=text)
    if status != 0 or body != expected:
        problems.append(f"{name} ({layout}): expected status 0 and {response}, got status {status} and {body!r}")

finish(problems, f"{name} ok in {len(LAYOUTS)} layouts")
