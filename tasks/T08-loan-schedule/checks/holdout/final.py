"""H4: the schedule ends in the right month, and the last payment clears the balance exactly (G3)."""

import random

from _cmd import call, finish
from _model import is_schedule, random_loan, schedule

rng = random.Random(8084)
loans = [
    (50, 0, 12), (13, 0, 12), (1, 0, 480), (479, 0, 480), (480, 0, 480), (5, 0, 3),  # interest-free, ends early
    (1000000, 5000, 480), (100000, 2400, 360), (100000, 1200, 360), (250000, 3000, 240),  # high rate, long term
    (700000, 500, 24), (2000000, 1075, 18), (750000, 400, 36), (200000, 975, 36),  # last payment above regular
    (1000000, 600, 12), (1, 1, 1), (1, 5000, 480), (1000000000, 5000, 480), (1000000000, 1, 480),
]
loans += [(p, 0, m) for p, m in ((rng.randint(1, 3000), rng.randint(2, 60)) for _ in range(20))]
loans += [(rng.randrange(10000, 300001, 100), rng.randrange(1500, 5001, 25), rng.choice((240, 300, 360, 480)))
          for _ in range(25)]
for _ in range(70):
    loan = random_loan(rng)
    loans.append((loan["principal_cents"], loan["annual_rate_bp"], loan["months"]))

early = sum(len(schedule(*loan)["rows"]) < loan[2] for loan in loans)
above = sum(schedule(*loan)["rows"][-1]["payment_cents"] > schedule(*loan)["payment_cents"] for loan in loans)
assert early >= 15 and above >= 10, ("check setup", early, above)

problems = []
for principal, rate, months in loans:
    name = f"{principal} cents at {rate} bp for {months} months"
    status, body = call({"principal_cents": principal, "annual_rate_bp": rate, "months": months})
    if status != 0 or not is_schedule(body):
        problems.append(f"{name}: expected a schedule, got status {status}")
        continue
    regular, rows = body.get("payment_cents"), body["rows"]
    if len(rows) > months:
        problems.append(f"{name}: {len(rows)} rows, more than {months} months")
        continue
    start = principal
    for number, row in enumerate(rows, start=1):
        paid, owed, left = row.get("payment_cents"), row.get("interest_cents"), row.get("balance_cents")
        if not all(isinstance(v, int) for v in (paid, owed, left, regular)):
            problems.append(f"{name}, row {number}: amounts must be whole numbers")
            break
        last = number == len(rows)
        can_finish = start + owed <= regular or number == months
        if not last and can_finish:
            problems.append(f"{name}: should end in month {number} (owes {start} + {owed} against a payment of "
                            f"{regular}), but continues to month {len(rows)}")
            break
        if not last and (paid != regular or left <= 0):
            problems.append(f"{name}, month {number}: before the last month, expected a payment of {regular} "
                            f"leaving a balance above 0, got {paid} leaving {left}")
            break
        if last and not can_finish:
            problems.append(f"{name}: ends in month {number} still owing {start} + {owed}, more than a payment of {regular}")
            break
        if last and (paid != start + owed or left != 0):
            problems.append(f"{name}: the last payment should be {start} + {owed} = {start + owed} leaving 0, "
                            f"got {paid} leaving {left}")
            break
        start = left

finish(problems, f"final payments ok: {len(loans)} loans, {early} finishing early, {above} ending above the regular payment")
