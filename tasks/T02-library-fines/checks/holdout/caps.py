"""H3: no single item's fine exceeds its type's cap, and late days past the cap add nothing (G3)."""

import random

from _cmd import call, finish
from _model import GRACE, ITEM_CAP, RATE, TYPES, fines_by_id, item

rng = random.Random(8080)
problems = []
cases = []
for kind in TYPES:
    at_cap = ITEM_CAP[kind] // RATE[kind]  # charged days that exactly reach the cap
    for charged in (at_cap - 1, at_cap, at_cap + 1, at_cap + 2, 2 * at_cap, 365, 1_000_000):
        cases.append((kind, GRACE[kind] + charged, min(charged * RATE[kind], ITEM_CAP[kind])))
    for _ in range(12):
        charged = rng.randint(at_cap + 1, 50_000)
        cases.append((kind, GRACE[kind] + charged, ITEM_CAP[kind]))

for kind, late, expected in cases:
    status, body = call({"items": [item("c", kind, rng.randint(0, 300), late)]})
    got = (fines_by_id(body) or {}).get("c") if status == 0 else None
    if got != expected:
        problems.append(f"{kind} {late} days late: expected {expected} cents, got {got!r} (status {status})")

finish(problems, f"item caps ok: {len(cases)} items")
