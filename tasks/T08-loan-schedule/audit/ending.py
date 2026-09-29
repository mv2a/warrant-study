"""X4 (G3): the schedule ends in the first month whose starting balance plus interest is at most the
regular payment, or in month n; the last payment is that month's starting balance plus its interest and
leaves 0; every earlier month pays exactly the regular payment and leaves a balance above 0.
Judged against the response's own regular payment and interest figures."""

import random

from _batch import call_all
from _cmd import finish
from _loan import req

CASES = [
    # finish before month n at a rate above zero
    (993, 1948, 88), (1361, 2308, 467), (3748, 131, 458), (2069, 3507, 360), (100, 100, 480),
    # finish before month n with a last payment exactly equal to the regular payment
    (71, 193, 381), (2343, 677, 353), (349, 819, 152), (326, 3339, 95), (3858, 27, 279),
    # a month where the balance alone fits in the payment but balance plus interest does not
    (2089, 3797, 348), (1745, 2156, 138), (455661817, 4751, 448), (1202, 4104, 244),
    # last month n pays more than the regular payment
    (4701, 3903, 391), (42574, 3460, 103), (352687657, 4757, 458),
    # last month n pays less than the regular payment
    (446347739, 234, 68), (4044, 3844, 13),
    # last month n pays exactly the regular payment
    (810549327, 3719, 18), (77796, 2719, 12), (3634, 435, 2),
    # regular payment no more than the interest: nothing repaid until a final balloon
    (1000000000, 5000, 480), (2901, 3391, 480), (82, 2840, 310),
    # one month, and loans of one cent
    (1, 1, 1), (123457, 777, 1), (1000000000, 5000, 1), (1, 2500, 480), (1, 0, 480),
    # interest-free loans that finish before month n
    (10, 0, 6), (7, 0, 5), (481, 0, 480), (1000, 0, 400),
]

rng = random.Random(2718)
for _ in range(40):
    size = rng.choice([(1, 3000), (3000, 3000000), (3000000, 1000000000)])
    CASES.append((rng.randint(*size), rng.choice([0] + [rng.randint(1, 5000)] * 6), rng.randint(1, 480)))

problems = []
early = 0
for (p, bp, n), (status, body) in zip(CASES, call_all([req(*c) for c in CASES])):
    name = req(p, bp, n)
    rows = body.get("rows") if isinstance(body, dict) else None
    regular = body.get("payment_cents") if isinstance(body, dict) else None
    if status != 0 or not isinstance(rows, list) or not rows or type(regular) is not int:
        problems.append(f"{name}: expected a schedule, got status {status} and {body!r}"[:300])
        continue
    if len(rows) > n:
        problems.append(f"{name}: {len(rows)} rows for a {n}-month loan")
        continue
    wrong = None
    start = p
    for number, row in enumerate(rows, start=1):
        try:
            pay, interest, after = row["payment_cents"], row["interest_cents"], row["balance_cents"]
        except (TypeError, KeyError):
            wrong = f"row {number} is not a schedule row: {row!r}"
            break
        if not all(type(v) is int for v in (pay, interest, after)):
            wrong = f"row {number} does not hold whole numbers: {row!r}"
            break
        fits = start + interest <= regular
        if number < len(rows):
            if fits:
                wrong = (f"month {number} starts owing {start} with {interest} interest, at most the regular "
                         f"payment {regular}, so the schedule must end there, but it goes on to month {len(rows)}")
            elif pay != regular:
                wrong = f"month {number} is not the last, so it pays the regular {regular}, got {pay!r}"
            elif not (type(after) is int and after > 0):
                wrong = f"month {number} is not the last, so it leaves a balance above 0, got {after!r}"
        else:
            if not fits and number < n:
                wrong = (f"the schedule stops at month {number} of {n}, but that month owes {start} plus "
                         f"{interest} interest, more than the regular payment {regular}")
            elif pay != start + interest:
                wrong = (f"the last payment (month {number}) must be its starting balance {start} plus its "
                         f"interest {interest}, that is {start + interest}, got {pay!r}")
            elif after != 0:
                wrong = f"the last payment (month {number}) must leave a balance of 0, got {after!r}"
        if wrong:
            break
        start = after
    if wrong:
        problems.append(f"{name}: {wrong}"[:300])
        continue
    if len(rows) < n:
        early += 1

finish(problems, f"ending ok: {len(CASES)} loans, {early} finished before month n")
