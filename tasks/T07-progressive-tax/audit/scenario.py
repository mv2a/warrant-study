"""X11 to X14 (S1 to S4): one scenario of intent.md, named on the command line, gives exactly
the stated response with exit status 0, the same on a second run."""

import sys

from _cmd import call, finish

SCENARIOS = {
    "S1": ({"income_cents": 3000000, "dependents": 0},
           {"income_cents": 3000000, "allowance_cents": 1200000, "taxable_cents": 1800000,
            "tax_before_credit_cents": 170000, "credit_cents": 0, "tax_cents": 170000}),
    "S2": ({"income_cents": 9500000, "dependents": 2},
           {"income_cents": 9500000, "allowance_cents": 900000, "taxable_cents": 8600000,
            "tax_before_credit_cents": 1650000, "credit_cents": 90000, "tax_cents": 1560000}),
    "S3": ({"income_cents": 1400000, "dependents": 3},
           {"income_cents": 1400000, "allowance_cents": 1200000, "taxable_cents": 200000,
            "tax_before_credit_cents": 10000, "credit_cents": 10000, "tax_cents": 0}),
    "S4": ({"income_cents": 1200030, "dependents": 0},
           {"income_cents": 1200030, "allowance_cents": 1200000, "taxable_cents": 30,
            "tax_before_credit_cents": 2, "credit_cents": 0, "tax_cents": 2}),
}

name = sys.argv[1]
request, want = SCENARIOS[name]
problems = []
for attempt in (1, 2):
    status, body = call(request)
    same_types = isinstance(body, dict) and all(type(body.get(k)) is int for k in want)
    if status != 0 or body != want or not same_types:
        problems.append(f"{name} run {attempt}: expected status 0 and {want}, got status {status} and {body!r}")

finish(problems, f"{name} ok")
