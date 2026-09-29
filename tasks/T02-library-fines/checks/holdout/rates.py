"""H1: each charged day costs the type's daily rate (G1)."""

import random

from _cmd import call, finish
from _model import GRACE, ITEM_CAP, RATE, TYPES, fines_by_id, item

rng = random.Random(20260929)
problems = []
cases = 0

# Every charged-day count below each type's cap, one item per request.
for kind in TYPES:
    for charged in range(1, ITEM_CAP[kind] // RATE[kind] + 1):
        late = GRACE[kind] + charged
        request = {"items": [item("x", kind, rng.randint(0, 5000), late)]}
        status, body = call(request)
        got = (fines_by_id(body) or {}).get("x") if status == 0 else None
        cases += 1
        if got != charged * RATE[kind]:
            problems.append(f"{kind} {late} days late: expected {charged * RATE[kind]} cents, got {got!r} (status {status})")

# Mixed requests: every item is fined at its own type's rate, whatever else is in the request.
for _ in range(25):
    items, expected = [], {}
    for n in range(rng.randint(2, 6)):
        kind = rng.choice(TYPES)
        charged = rng.randint(1, ITEM_CAP[kind] // RATE[kind])
        ident = f"{kind[0]}{n}"
        items.append(item(ident, kind, rng.randint(0, 900), GRACE[kind] + charged))
        expected[ident] = charged * RATE[kind]
    status, body = call({"items": items})
    got = fines_by_id(body) if status == 0 else None
    cases += 1
    if got != expected:
        problems.append(f"{items}: expected item fines {expected}, got {got!r} (status {status})")

finish(problems, f"rates ok: {cases} requests")
