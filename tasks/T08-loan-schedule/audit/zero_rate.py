"""X5 (G4): interest-free loans (a yearly rate of 0) are scheduled: every month's interest is 0 and the
regular payment is the amount borrowed divided by the number of months, rounded up to a whole cent."""

import random

from _batch import call_all
from _cmd import finish
from _loan import ceil_div, req

CASES = [
    (120, 12), (1200000, 480), (1000000000, 480), (1000000000, 1), (1000000000, 7), (999999999, 7),
    (1, 1), (1, 480), (479, 480), (480, 480), (481, 480), (10, 6), (7, 5), (5, 3), (2, 3),
    (123456789, 360), (987654321, 13), (1001, 333), (59, 59), (60, 59),
]
rng = random.Random(6060)
for _ in range(30):
    size = rng.choice([(1, 1000), (1000, 1000000), (1000000, 1000000000)])
    CASES.append((rng.randint(*size), rng.randint(1, 480)))

problems = []
for (p, n), (status, body) in zip(CASES, call_all([req(p, 0, n) for p, n in CASES])):
    name = req(p, 0, n)
    rows = body.get("rows") if isinstance(body, dict) else None
    if status != 0 or not isinstance(rows, list) or not rows:
        problems.append(f"{name}: an interest-free loan must be scheduled, got status {status} and {body!r}"[:300])
        continue
    wanted = ceil_div(p, n)
    if body.get("payment_cents") != wanted:
        problems.append(f"{name}: regular payment must be {p} / {n} rounded up, {wanted}, got {body.get('payment_cents')!r}")
    charged = [(number, row.get("interest_cents") if isinstance(row, dict) else row)
               for number, row in enumerate(rows, start=1)]
    charged = [(number, v) for number, v in charged if not (type(v) is int and v == 0)]
    if charged:
        problems.append(f"{name}: interest must be 0 every month, month {charged[0][0]} has {charged[0][1]!r}")

finish(problems, f"interest-free ok: {len(CASES)} loans")
