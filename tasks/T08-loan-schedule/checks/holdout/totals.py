"""H6: the total interest is the sum of the rows, and the rows add up to the loan (C2)."""

import random

from _cmd import call, finish
from _model import is_schedule, random_loan

rng = random.Random(8086)
loans = [
    {"principal_cents": 1000000, "annual_rate_bp": 600, "months": 12},
    {"principal_cents": 700000, "annual_rate_bp": 500, "months": 24},
    {"principal_cents": 100000, "annual_rate_bp": 0, "months": 7},
    {"principal_cents": 50, "annual_rate_bp": 0, "months": 12},
    {"principal_cents": 1000000000, "annual_rate_bp": 5000, "months": 480},
    {"principal_cents": 1, "annual_rate_bp": 1, "months": 1},
] + [random_loan(rng) for _ in range(90)]

problems = []
for loan in loans:
    status, body = call(loan)
    if status != 0 or not is_schedule(body):
        problems.append(f"{loan}: expected a schedule, got status {status}")
        continue
    rows = body["rows"]
    try:
        interest = sum(row["interest_cents"] for row in rows)
        principal = sum(row["principal_cents"] for row in rows)
        paid = sum(row["payment_cents"] for row in rows)
    except (KeyError, TypeError):
        problems.append(f"{loan}: rows must carry whole-number amounts")
        continue
    total = body.get("total_interest_cents")
    if total != interest:
        problems.append(f"{loan}: total_interest_cents is {total!r}, but the rows' interest adds up to {interest}")
    elif principal != loan["principal_cents"]:
        problems.append(f"{loan}: the rows' principal adds up to {principal}, not the {loan['principal_cents']} borrowed")
    elif paid != loan["principal_cents"] + total:
        problems.append(f"{loan}: the payments add up to {paid}, not {loan['principal_cents']} + {total}")

finish(problems, f"totals ok: {len(loans)} loans")
