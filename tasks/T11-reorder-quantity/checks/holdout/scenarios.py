"""H8 (S1, S2, S3): the intent's three scenarios, sent compact and pretty-printed."""

import json

from _cmd import call, finish
from _model import product


def order(sku, wanted, quantity, cost_cents):
    return {"sku": sku, "wanted": wanted, "quantity": quantity, "cost_cents": cost_cents}


SCENARIOS = [
    ("S1",
     {"budget_cents": 100000, "products": [product("BOLT-M6", 20, 12, 8, 5, 15, 24, 35, 1)]},
     {"orders": [order("BOLT-M6", 24, 24, 840)], "total_cost_cents": 840, "budget_left_cents": 99160}),
    ("S2",
     {"budget_cents": 3500, "products": [
         product("OF-220", 4, 0, 2, 7, 6, 10, 150, 2),
         product("GK-110", 10, 5, 3, 6, 8, 6, 100, 1),
         product("HS-300", 0, 0, 1, 10, 2, 5, 400, 3)]},
     {"orders": [order("OF-220", 20, 10, 1500), order("GK-110", 12, 12, 1200), order("HS-300", 15, 0, 0)],
      "total_cost_cents": 2700, "budget_left_cents": 800}),
    ("S3",
     {"budget_cents": 0, "products": [
         product("WS-40", 30, 10, 5, 4, 20, 12, 90, 1),
         product("WS-41", 0, 0, 1, 3, 0, 4, 250, 2)]},
     {"orders": [order("WS-40", 0, 0, 0), order("WS-41", 4, 0, 0)], "total_cost_cents": 0, "budget_left_cents": 0}),
]
problems = []
for name, request, want in SCENARIOS:
    for style, raw in (("compact", json.dumps(request, separators=(",", ":"))),
                       ("pretty-printed", json.dumps(request, indent=2, sort_keys=True))):
        status, body = call(raw=raw)
        if status != 0 or body != want:
            problems.append(f"{name} ({style}): expected status 0 and {want}, got status {status} and {body!r}")

finish(problems, "scenarios ok: S1, S2, S3, each sent two ways")
