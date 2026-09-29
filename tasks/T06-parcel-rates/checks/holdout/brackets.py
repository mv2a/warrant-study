"""H2 (G2): up to 10,000 g, the base price is the table price of the lightest bracket that holds the billable weight."""

import random

from _cmd import call, finish
from _model import base, billable, exact, parcel, random_parcel

rng = random.Random(6020)
WEIGHTS = [1, 250, 499, 500, 501, 999, 1000, 1001, 1999, 2000, 2001, 4999, 5000, 5001, 9999, 10000]
cases = [parcel(zone, w, (1, 1, 1)) for zone in (1, 2, 3, 4) for w in WEIGHTS]
cases += [  # billable weight set by the dimensions, on and just over the bracket edges
    parcel(1, 1, (25, 10, 10)),   # 500 g
    parcel(2, 1, (15, 14, 12)),   # 504 g
    parcel(3, 1, (25, 20, 10)),   # 1000 g
    parcel(4, 1, (35, 13, 11)),   # 1001 g
    parcel(1, 1, (25, 20, 20)),   # 2000 g
    parcel(2, 1, (29, 23, 15)),   # 2001 g
    parcel(3, 1, (50, 25, 20)),   # 5000 g
    parcel(4, 1, (61, 41, 10)),   # 5002 g
    parcel(1, 1, (50, 50, 20)),   # 10000 g
]
# Generated parcels whose billable weight needs no rounding, so that this check tests the brackets (G2), not G1.
cases += [random_parcel(rng, lambda p: billable(p) <= 10000 and exact(p)) for _ in range(50)]
problems = []
for p in cases:
    want = base(p["zone"], billable(p))
    status, body = call(p)
    got = body.get("base_cents") if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(f"{p} (billable {billable(p)} g): expected base_cents {want}, got status {status} and {got!r}")

finish(problems, f"weight brackets ok: {len(cases)} parcels")
