"""H3 (G3): 450.00 of non-refundable credit per dependent, never taking the tax below zero."""

import random

from _cmd import call, finish
from _model import CREDIT_PER_DEPENDENT, whole

rng = random.Random(70703)
cases = [
    (2_100_000, 1),   # tax 450.00, credit 450.00: exactly used up
    (2_100_001, 1),   # tax rounds to 450.00 again
    (2_100_020, 1),   # tax 450.01: one cent left to pay
    (3_000_000, 0),   # no dependents, no credit
    (3_000_000, 20),  # 9,000.00 of credit against 1,700.00 of tax
    (0, 20),          # no income: no tax, no credit used
    (1_200_000, 5),   # income equal to the allowance
    (1_400_000, 3),
    (9_500_000, 2),
    (10**9, 20),
] + [(rng.randint(0, 3_500_000), rng.randint(0, 20)) for _ in range(35)] \
  + [(rng.randint(0, 20_000_000), rng.randint(0, 20)) for _ in range(35)]

problems = []
for income, dependents in cases:
    status, body = call({"income_cents": income, "dependents": dependents})
    if status != 0 or not isinstance(body, dict):
        problems.append(f"income {income}, {dependents} dependents: expected a response, got status {status} and {body!r}")
        continue
    before, credit, tax = body.get("tax_before_credit_cents"), body.get("credit_cents"), body.get("tax_cents")
    if not (whole(before) and whole(credit) and whole(tax)):
        problems.append(f"income {income}, {dependents} dependents: amounts must be integers, got {body!r}")
        continue
    available = CREDIT_PER_DEPENDENT * dependents
    used = min(available, max(0, before))
    if credit != used or tax != max(0, before - available):
        problems.append(
            f"income {income}, {dependents} dependents: tax before credit {before} and {available} of credit "
            f"should give credit {used} and tax {max(0, before - available)}, got credit {credit} and tax {tax}"
        )

finish(problems, f"credit ok: {len(cases)} filers")
