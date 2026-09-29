"""X6 (C2): total_interest_cents is the sum of the rows' interest, the rows' principal adds up to exactly
the amount borrowed, and the rows' payments add up to the amount borrowed plus the total interest."""

import random

from _batch import call_all
from _cmd import finish
from _loan import req

CASES = [
    (1000000000, 5000, 480), (1000000000, 1, 480), (1, 1, 1), (1, 5000, 480), (1, 0, 480),
    (10, 0, 6), (1000000000, 0, 480), (123457, 777, 1), (2901, 3391, 480), (993, 1948, 88),
    (77796, 2719, 12), (446347739, 234, 68),
]
rng = random.Random(777)
for _ in range(48):
    size = rng.choice([(1, 10000), (10000, 10000000), (10000000, 1000000000)])
    rate = rng.choice([0, rng.randint(1, 800), rng.randint(800, 5000), rng.randint(1, 5000)])
    CASES.append((rng.randint(*size), rate, rng.randint(1, 480)))

problems = []
for (p, bp, n), (status, body) in zip(CASES, call_all([req(*c) for c in CASES])):
    name = req(p, bp, n)
    rows = body.get("rows") if isinstance(body, dict) else None
    if status != 0 or not isinstance(rows, list) or not rows:
        problems.append(f"{name}: expected a schedule, got status {status} and {body!r}"[:300])
        continue
    try:
        interest = sum(r["interest_cents"] for r in rows)
        principal = sum(r["principal_cents"] for r in rows)
        paid = sum(r["payment_cents"] for r in rows)
    except (TypeError, KeyError):
        problems.append(f"{name}: rows do not all hold interest, principal and payment amounts")
        continue
    total = body.get("total_interest_cents")
    if total != interest:
        problems.append(f"{name}: total_interest_cents {total!r} is not the rows' interest summed, {interest}")
    if principal != p:
        problems.append(f"{name}: the rows' principal adds up to {principal}, not the {p} borrowed")
    if paid != p + interest or (type(total) is int and paid != p + total):
        problems.append(f"{name}: the rows' payments add up to {paid}, not the {p} borrowed plus "
                        f"the total interest {total!r}")

finish(problems, f"totals ok: {len(CASES)} loans")
