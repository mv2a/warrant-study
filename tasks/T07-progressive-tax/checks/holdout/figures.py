"""H5 (C2): taxable = income - allowance (never below zero), tax = tax before credit - credit, income repeated."""

import random

from _cmd import call, finish
from _model import whole

rng = random.Random(70705)
incomes = [0, 1, 500_000, 1_199_999, 1_200_000, 1_200_001, 8_000_003, 13_999_999, 14_000_000, 10**13]
incomes += [rng.randint(0, 1_200_000) for _ in range(25)] + [rng.randint(0, 40_000_000) for _ in range(45)]

problems = []
for income in incomes:
    dependents = rng.randint(0, 20)
    status, body = call({"income_cents": income, "dependents": dependents})
    if status != 0 or not isinstance(body, dict):
        problems.append(f"income {income}: expected a response, got status {status} and {body!r}")
        continue
    values = [body.get(k) for k in ("income_cents", "allowance_cents", "taxable_cents", "tax_before_credit_cents", "credit_cents", "tax_cents")]
    if not all(whole(v) for v in values):
        problems.append(f"income {income}: every figure must be an integer, got {body!r}")
        continue
    echoed, allowed, taxable, before, credit, tax = values
    if echoed != income:
        problems.append(f"income {income}: income_cents must repeat the request, got {echoed}")
    if taxable != max(0, income - allowed):
        problems.append(f"income {income}, allowance {allowed}: taxable income should be {max(0, income - allowed)}, got {taxable}")
    if tax != before - credit:
        problems.append(f"income {income}: tax should be {before} - {credit} = {before - credit}, got {tax}")

finish(problems, f"figures ok: {len(incomes)} filers")
