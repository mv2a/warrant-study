"""H1 (G1): taxable income is taxed in marginal bands of 5%, 15%, 25% and 38%."""

import math
import random

from _cmd import call, finish
from _model import STANDARD_ALLOWANCE, exact_band_tax, income_for_taxable, whole

rng = random.Random(70701)
# Below 80,000.00 of income the full allowance applies, so taxable = income - 12,000.00.
full_allowance = [t + STANDARD_ALLOWANCE for t in (
    0, 1, 500_000, 999_999, 1_000_000, 1_000_001, 2_500_000,
    3_999_999, 4_000_000, 4_000_001, 5_500_000, 6_799_999,
)]
# Inside the phase-out, around the 100,000.00 edge of the top band.
phase_out = [income_for_taxable(t) for t in (9_999_998, 10_000_000, 10_000_001, 10_000_003)] + [9_000_000, 12_345_678]
# From 140,000.00 up there is no allowance, so the whole income is taxable.
no_allowance = [14_000_000, 14_000_001, 20_000_000, 50_000_000, 123_456_789, 10**12]
randoms = [rng.randint(0, 30_000_000) for _ in range(50)] + [rng.randint(30_000_000, 10**11) for _ in range(10)]
incomes = full_allowance + phase_out + no_allowance + randoms

problems = []
for income in incomes:
    dependents = rng.randint(0, 20)
    status, body = call({"income_cents": income, "dependents": dependents})
    if status != 0 or not isinstance(body, dict):
        problems.append(f"income {income}, {dependents} dependents: expected a response, got status {status} and {body!r}")
        continue
    taxable, before = body.get("taxable_cents"), body.get("tax_before_credit_cents")
    if not whole(taxable) or not whole(before):
        problems.append(f"income {income}: taxable_cents and tax_before_credit_cents must be integers, got {body!r}")
        continue
    # Rounding is C1's business: here either neighbouring cent of the exact band tax is accepted.
    exact = exact_band_tax(taxable)
    if before not in (math.floor(exact), math.ceil(exact)):
        problems.append(f"taxable {taxable} (income {income}): band tax is {float(exact):.2f} cents, got tax_before_credit_cents {before}")

finish(problems, f"bands ok: {len(incomes)} incomes")
