"""H3: each month's interest is the starting balance times i, to the nearest cent with halves up,
and the rest of the payment pays down the balance (G2)."""

import random

from _cmd import call, finish
from _model import interest, is_schedule, random_loan, random_months, random_principal

rng = random.Random(8083)

# Month 1 interest where the rounding matters: (principal, rate, months, expected month-1 interest).
FIRST_MONTH = [
    (100, 600, 12, 1),         # 0.5 cent rounds up
    (300, 600, 6, 2),          # 1.5 cents round up
    (1000100, 600, 12, 5001),  # 5000.5 cents round up
    (25, 2400, 3, 1),          # 0.5 cent
    (20, 3000, 1, 1),          # 0.5 cent
    (59999, 1, 2, 0),          # 0.49999 cent rounds down
    (60000, 1, 2, 1),          # exactly 0.5 cent
    (180000, 1, 2, 2),         # exactly 1.5 cents
    (1, 5000, 1, 0),           # 0.0417 cent
    (11, 5000, 1, 0),          # 0.4583 cent
    (13, 5000, 1, 1),          # 0.5417 cent
    (1234567, 777, 60, 7994),  # 7993.82 cents
]
for principal, rate, months, expected in FIRST_MONTH:
    assert interest(principal, rate) == expected, ("check setup", principal, rate)

# Rates at which half cents come up often, and fully random loans.
HALVING_RATES = (150, 300, 600, 750, 1200, 1500, 2400, 3000, 4800)
loans = [{"principal_cents": p, "annual_rate_bp": r, "months": m} for p, r, m, _ in FIRST_MONTH]
loans += [{"principal_cents": random_principal(rng), "annual_rate_bp": rng.choice(HALVING_RATES),
           "months": random_months(rng)} for _ in range(60)]
loans += [random_loan(rng) for _ in range(60)]

problems = []
rows_checked = 0
for loan in loans:
    rate = loan["annual_rate_bp"]
    status, body = call(loan)
    if status != 0 or not is_schedule(body):
        problems.append(f"{loan}: expected a schedule, got status {status}")
        continue
    start = loan["principal_cents"]
    for row in body["rows"]:
        month = row.get("month")
        expected = interest(start, rate)
        paid, owed, down, left = (row.get(k) for k in ("payment_cents", "interest_cents", "principal_cents", "balance_cents"))
        rows_checked += 1
        if owed != expected:
            problems.append(f"{loan}, month {month}: interest on {start} should be {expected}, got {owed!r}")
            break
        if not (isinstance(paid, int) and isinstance(down, int)) or down != paid - owed:
            problems.append(f"{loan}, month {month}: principal should be payment {paid!r} minus interest {owed}, got {down!r}")
            break
        if left != start - down:
            problems.append(f"{loan}, month {month}: balance should be {start} - {down} = {start - down}, got {left!r}")
            break
        start = left

finish(problems, f"interest ok: {len(loans)} loans, {rows_checked} months")
