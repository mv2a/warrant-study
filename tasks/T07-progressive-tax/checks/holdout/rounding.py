"""H4 (C1): the band tax is rounded to the nearest cent with halves up; the allowance reduction is rounded up."""

import math
import random

from _cmd import call, finish
from _model import STANDARD_ALLOWANCE, allowance, exact_band_tax, half_up, whole

rng = random.Random(70704)

# Part 1: tax rounding. Taxable incomes whose band tax ends in a fraction of a cent, many of them an
# exact half with an even cent below it, where rounding half to even would go the wrong way.
BAND_START = {1: 0, 2: 1_000_000, 3: 4_000_000, 4: 10_000_000}
HALF = {1: (20, 10), 2: (20, 10), 3: (4, 2), 4: (50, 25)}  # (modulus, remainder) that makes an exact half cent
taxables = [1, 9, 10, 11, 19, 30, 50, 70, 90, 999_990,
            1_000_001, 1_000_003, 1_000_004, 1_000_010, 1_000_030,
            4_000_001, 4_000_002, 4_000_003, 4_000_010,
            14_000_025, 14_000_075, 14_000_001]
# The part of taxable income inside each band that the generated cases use. Bands 1 to 3 stay below
# 68,000.00 of taxable income (full allowance); band 4 starts at 140,000.00 (no allowance).
PART = {1: (0, 999_999), 2: (0, 2_999_999), 3: (0, 2_799_999), 4: (4_000_000, 30_000_000)}
for band in (1, 2, 3, 4):
    modulus, remainder = HALF[band]
    low, top = PART[band]
    for _ in range(20):
        part = rng.randint(low // modulus, top // modulus - 1) * modulus + remainder
        taxables.append(BAND_START[band] + part)
    for _ in range(4):
        taxables.append(BAND_START[band] + rng.randint(max(1, low), top))

def income_for(taxable):
    # Below 80,000.00 of income taxable = income - 12,000.00; from 140,000.00 up taxable = income.
    if taxable < 6_800_000:
        return taxable + STANDARD_ALLOWANCE
    assert taxable >= 14_000_000, taxable
    return taxable

problems = []
judged = 0
for taxable in taxables:
    income = income_for(taxable)
    status, body = call({"income_cents": income, "dependents": rng.randint(0, 20)})
    got_taxable = body.get("taxable_cents") if isinstance(body, dict) else None
    before = body.get("tax_before_credit_cents") if isinstance(body, dict) else None
    if status != 0 or not whole(got_taxable) or not whole(before):
        problems.append(f"income {income}: expected whole-cent taxable and tax figures, got status {status} and {body!r}")
        continue
    exact = exact_band_tax(got_taxable)
    if abs(before - exact) > 1:
        continue  # more than a cent off is a banding error, which H1 (G1) reports; rounding can't be judged here
    judged += 1
    if before != half_up(exact):
        problems.append(f"taxable {got_taxable}: exact tax {exact.numerator}/{exact.denominator} cents rounds to {half_up(exact)}, got {before}")
if judged < 80:
    problems.append(f"only {judged} of {len(taxables)} tax amounts were within a cent of the band tax, too few to judge the rounding")

# Part 2: the allowance reduction, one fifth of the income above 80,000.00, rounded up to a whole cent.
incomes = [8_000_001, 8_000_004, 8_000_005, 8_000_006, 8_000_009, 8_000_010, 13_999_995, 13_999_996, 13_999_999]
incomes += [rng.randint(8_000_001, 13_999_999) for _ in range(40)]
for income in incomes:
    status, body = call({"income_cents": income, "dependents": 0})
    got = body.get("allowance_cents") if isinstance(body, dict) else None
    if status != 0 or got != allowance(income, math.ceil):
        problems.append(f"income {income}: expected an allowance of {allowance(income, math.ceil)}, got status {status} and {got!r}")

finish(problems, f"rounding ok: {judged} of {len(taxables)} tax amounts and {len(incomes)} allowances")
