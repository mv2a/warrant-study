"""H1: the command reads one JSON object and writes one JSON object shaped exactly as C1 says."""

import json
import random

from _cmd import call, call_exact, finish
from _model import MAX_MONTHS, MAX_PRINCIPAL, MAX_RATE, random_loan

TOP = {"payment_cents", "total_interest_cents", "rows"}
ROW = {"month", "payment_cents", "interest_cents", "principal_cents", "balance_cents"}

rng = random.Random(8081)
loans = [
    {"principal_cents": 1, "annual_rate_bp": 0, "months": 1},
    {"principal_cents": MAX_PRINCIPAL, "annual_rate_bp": MAX_RATE, "months": MAX_MONTHS},
    {"principal_cents": 1, "annual_rate_bp": MAX_RATE, "months": MAX_MONTHS},
    {"principal_cents": MAX_PRINCIPAL, "annual_rate_bp": 0, "months": 1},
    {"principal_cents": 123456, "annual_rate_bp": 1, "months": 360},
] + [random_loan(rng) for _ in range(25)]
problems = []


def shape_problem(body):
    if not isinstance(body, dict) or set(body) != TOP:
        return f"expected an object with exactly {sorted(TOP)}, got {str(body)[:120]}"
    for key in ("payment_cents", "total_interest_cents"):
        if type(body[key]) is not int:
            return f"{key} must be a whole number, got {body[key]!r}"
    rows = body["rows"]
    if not isinstance(rows, list) or not rows:
        return f"rows must be a non-empty list, got {str(rows)[:120]}"
    for number, row in enumerate(rows, start=1):
        if not isinstance(row, dict) or set(row) != ROW:
            return f"row {number} must have exactly {sorted(ROW)}, got {str(row)[:120]}"
        bad = [key for key in sorted(ROW) if type(row[key]) is not int]
        if bad:
            return f"row {number}: {', '.join(bad)} must be whole numbers, got {row!r}"
        if row["month"] != number:
            return f"row {number} is numbered {row['month']!r}; months count 1, 2, 3, ..."
    return None


for index, loan in enumerate(loans):
    if index % 3 == 0:
        # Field order and layout must not matter: send the fields reversed and pretty-printed.
        raw = json.dumps(dict(reversed(list(loan.items()))), indent=2) + "\n"
        status, body = call(raw=raw)
    else:
        status, body = call(loan)
    if status != 0:
        problems.append(f"{loan}: exited with status {status}, expected 0")
        continue
    problem = shape_problem(body)
    if problem:
        problems.append(f"{loan}: {problem}")

# Fields beyond the three in C1 are ignored: the loan is scheduled exactly as if they were not there.
PLAIN = {"principal_cents": 480000, "annual_rate_bp": 399, "months": 60}
EXTRAS = [
    ("a currency", {"currency": "USD"}, False),
    ("a note of null", {"note": None}, True),
    ("a fee and a list of tags", {"fee_cents": 1500, "tags": ["car", "new"]}, False),
    ("a field named Months", {"Months": 999}, True),
    ("a nested object", {"loan": {"principal_cents": 1, "annual_rate_bp": 0, "months": 1}}, False),
]
status, plain = call(PLAIN)
if status != 0 or shape_problem(plain):
    problems.append(f"{PLAIN}: expected a schedule, got status {status} and {str(plain)[:80]}")
else:
    for name, extra, first in EXTRAS:
        request = {**extra, **PLAIN} if first else {**PLAIN, **extra}
        status, body = call(request)
        if status != 0 or body != plain:
            problems.append(f"a request with {name} must be scheduled as if that field were not there, "
                            f"got status {status} and {'another schedule' if status == 0 else str(body)[:80]}")

REFUSED = [
    ("0 months", '{"principal_cents": 100000, "annual_rate_bp": 500, "months": 0}'),
    ("a negative amount", '{"principal_cents": -100, "annual_rate_bp": 500, "months": 12}'),
    ("a rate of 5001", '{"principal_cents": 100000, "annual_rate_bp": 5001, "months": 12}'),
    ("a missing principal", '{"annual_rate_bp": 500, "months": 12}'),
    ("months written as text", '{"principal_cents": 100000, "annual_rate_bp": 500, "months": "12"}'),
    ("empty input", ""),
    ("text that is not JSON", "borrow ten thousand"),
    ("a list", "[100000, 500, 12]"),
]
for name, raw in REFUSED:
    status, out = call_exact(raw=raw)
    if status != 2 or out != "":
        problems.append(f"{name}: a refusal must exit with status 2 and write nothing on standard output, "
                        f"got status {status} and {str(out)[:80]!r}")

finish(problems, f"interface ok: {len(loans)} schedules, {len(EXTRAS)} with extra fields, {len(REFUSED)} refusals")
