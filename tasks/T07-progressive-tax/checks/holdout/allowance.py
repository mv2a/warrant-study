"""H2 (G2): the 12,000.00 allowance shrinks by a fifth of the income above 80,000.00 and never goes below zero."""

import math
import random

from _cmd import call, finish
from _model import allowance, whole

rng = random.Random(70702)
incomes = [
    0, 1, 1_200_000, 5_000_000, 7_999_999, 8_000_000, 8_000_001, 8_000_005, 8_000_010,
    9_500_000, 11_000_000, 13_999_995, 13_999_999, 14_000_000, 14_000_001, 15_000_000,
    20_000_000, 100_000_000, 10**12,
] + [rng.randint(0, 25_000_000) for _ in range(55)] + [rng.randint(8_000_001, 13_999_999) for _ in range(15)]

problems = []
for income in incomes:
    dependents = rng.randint(0, 20)
    status, body = call({"income_cents": income, "dependents": dependents})
    got = body.get("allowance_cents") if isinstance(body, dict) else None
    # C1 decides how a fractional cent of reduction is rounded; this check accepts either direction.
    accepted = {allowance(income, math.ceil), allowance(income, math.floor)}
    if status != 0 or not whole(got) or got not in accepted:
        problems.append(f"income {income}: expected an allowance of {sorted(accepted)}, got status {status} and {got!r}")

finish(problems, f"allowance ok: {len(incomes)} incomes")
