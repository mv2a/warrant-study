"""H1 (G1): billable weight is the greater of actual and dimensional weight, rounded up to a gram."""

import random

from _cmd import call, finish
from _model import billable, parcel, random_parcel

rng = random.Random(6010)
cases = [
    parcel(1, 1, (1, 1, 1)),        # 0.2 g of volume rounds up to 1 g
    parcel(2, 1, (1, 1, 3)),        # 0.6 g rounds up to 1 g
    parcel(3, 1, (2, 2, 2)),        # 1.6 g rounds up to 2 g
    parcel(4, 486, (17, 13, 11)),   # 486.2 g rounds up to 487 g, just above the actual weight
    parcel(1, 1000, (25, 20, 10)),  # both exactly 1000 g
    parcel(2, 1001, (25, 20, 10)),  # actual weight wins by a gram
    parcel(3, 999, (25, 20, 10)),   # dimensional weight wins by a gram
    parcel(4, 1000, (31, 29, 7)),   # 1258.6 g rounds up to 1259 g
    parcel(1, 12000, (40, 30, 20)), # heavy and compact: actual weight wins
    parcel(2, 50, (7, 11, 13)),     # 200.2 g rounds up to 201 g
]
cases += [random_parcel(rng) for _ in range(80)]
cases += [random_parcel(rng, lambda p: p["weight_g"] < 500) for _ in range(40)]
problems = []
for p in cases:
    want = billable(p)
    status, body = call(p)
    got = body.get("billable_g") if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(f"{p}: expected billable_g {want}, got status {status} and {got!r}")

finish(problems, f"billable weight ok: {len(cases)} parcels")
