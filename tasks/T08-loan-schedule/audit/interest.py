"""X3 (G2): every month's interest is its starting balance times i, rounded to the nearest cent with
an exact half cent rounded up; the rest of the payment is principal; the balance after is the starting
balance minus that principal; month 1 starts from the amount borrowed, later months from the balance
the month before left. Checked row by row against each row's own payment."""

import random

from _batch import call_all
from _cmd import finish
from _loan import interest_on, req

# Month 1 interest is exactly k + 1/2 cents with k even, so rounding half to even would round down.
HALF_FIRST = [
    (2000, 30, 12), (2400, 125, 9), (1250, 240, 30), (1440, 375, 2), (1125, 480, 60), (1300, 600, 12),
    (1040, 750, 3), (1020, 1000, 18), (1050, 1200, 24), (1160, 1500, 5), (1110, 2000, 36), (1025, 2400, 7),
    (1060, 3000, 11), (1040, 3750, 4), (1035, 4000, 25), (1020, 5000, 48),
]
# Loans that meet an exact half cent of interest in several later months.
HALF_LATER = [
    (4721551, 3000, 120), (1692533, 3000, 89), (3461504, 1200, 117), (4874649, 3000, 97),
    (4112418, 2400, 112), (1372098, 3000, 119), (4413469, 2400, 96), (4125767, 3000, 63),
]
EDGES = [(1, 5000, 480), (1000000000, 5000, 480), (1000000000, 1, 480), (59999, 1, 3), (60000, 1, 3),
         (60001, 1, 3), (23, 2609, 1), (100000, 0, 9)]

rng = random.Random(5150)
GENERATED = []
for _ in range(36):
    size = rng.choice([(1, 20000), (20000, 20000000), (20000000, 1000000000)])
    GENERATED.append((rng.randint(*size), rng.randint(1, 5000), rng.randint(1, 240)))

cases = HALF_FIRST + HALF_LATER + EDGES + GENERATED
problems = []
halves = 0
for (p, bp, n), (status, body) in zip(cases, call_all([req(*c) for c in cases])):
    name = req(p, bp, n)
    rows = body.get("rows") if isinstance(body, dict) else None
    if status != 0 or not isinstance(rows, list) or not rows:
        problems.append(f"{name}: expected a schedule, got status {status} and {body!r}"[:300])
        continue
    start = p
    for number, row in enumerate(rows, start=1):
        try:
            pay, interest, principal, after = (row["payment_cents"], row["interest_cents"],
                                               row["principal_cents"], row["balance_cents"])
        except (TypeError, KeyError):
            problems.append(f"{name}: row {number} is not a schedule row: {row!r}"[:300])
            break
        if not all(type(v) is int for v in (pay, interest, principal, after)):
            problems.append(f"{name}: row {number} does not hold whole numbers: {row!r}"[:300])
            break
        wanted = interest_on(start, bp)
        if (2 * start * bp) % 240000 == 120000:
            halves += 1
        if interest != wanted:
            problems.append(f"{name}: month {number} starts owing {start}, so interest is {wanted}, got {interest!r}")
            break
        if principal != pay - interest:
            problems.append(f"{name}: month {number} pays {pay} with {interest} interest, so principal is "
                            f"{pay - interest}, got {principal!r}")
            break
        if after != start - principal:
            problems.append(f"{name}: month {number} starts owing {start} and repays {principal}, so the balance "
                            f"after is {start - principal}, got {after!r}")
            break
        start = after

finish(problems, f"interest ok: {len(cases)} loans, every row, including {halves} exact half cents")
