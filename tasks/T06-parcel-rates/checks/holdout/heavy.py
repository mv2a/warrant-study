"""H3 (G3): over 10,000 g, the 10,000 g price plus the zone's rate for every started kilogram above it."""

import random

from _cmd import call, finish
from _model import base, billable, exact, parcel, random_parcel

rng = random.Random(6030)
WEIGHTS = [10001, 10500, 10999, 11000, 11001, 12000, 12001, 15500, 19999, 20000, 20001, 25000, 29001, 29999, 30000]
cases = [parcel(zone, w, (1, 1, 1)) for zone in (1, 2, 3, 4) for w in WEIGHTS]
cases += [  # billable weight set by the dimensions
    parcel(1, 1, (137, 73, 5)),   # 10001 g: one extra kilogram
    parcel(2, 1, (50, 50, 22)),   # 11000 g: one extra kilogram
    parcel(3, 1, (131, 21, 20)),  # 11004 g: two extra kilograms
    parcel(4, 1, (113, 59, 15)),  # 20001 g: eleven extra kilograms
    parcel(1, 1, (100, 50, 30)),  # 30000 g: twenty extra kilograms
]
# Generated parcels whose billable weight needs no rounding, so that this check tests G3, not G1.
cases += [random_parcel(rng, lambda p: billable(p) > 10000 and exact(p)) for _ in range(50)]
problems = []
for p in cases:
    want = base(p["zone"], billable(p))
    status, body = call(p)
    got = body.get("base_cents") if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(f"{p} (billable {billable(p)} g): expected base_cents {want}, got status {status} and {got!r}")

finish(problems, f"heavy parcels ok: {len(cases)} parcels")
