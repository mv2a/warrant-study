"""X7 (C1): generated filers (fixed seed) built to land on exact half cents in every band,
plus filers in the allowance taper and at random. The tax before credit must be the exact
band tax on the reported taxable income rounded half up, and in the taper the allowance
must reflect a reduction rounded up to the next whole cent.

Only the rounding is judged here. A tax before credit more than a cent away from the exact
band tax on the reported taxable income (beyond one part in 10**14 for amounts far past
ordinary incomes) is a band error, G1's business; an allowance outside the two whole cents
around the exact G2 allowance, or the full 12,000.00 above 80,000.00 of income (no phase-out
applied at all), is a phase-out error, G2's business. Neither is judged here."""

import random

from _cmd import finish
from _model import (STANDARD_ALLOWANCE, TAPER_END, TAPER_FROM, allowance, allowance_either_rounding,
                    band_hundredths, half_up, near_band_tax, taxed)

rng = random.Random(7_702_319)
incomes = []
# taxable income on an exact half cent in each band (standard allowance, or none above 140,000.00)
incomes += [1_200_000 + 20 * rng.randint(0, 49_999) + 10 for _ in range(14)]                 # 5% band
incomes += [2_200_000 + 20 * rng.randint(0, 149_999) + 10 for _ in range(14)]                # 15% band
incomes += [5_200_000 + 4 * rng.randint(0, 699_999) + 2 for _ in range(14)]                  # 25% band
incomes += [10_000_000 + 50 * rng.randint(80_000, 2_000_000_000) + 25 for _ in range(14)]    # 38% band
# the taper, where both roundings happen
incomes += [rng.randint(TAPER_FROM + 1, TAPER_END - 1) for _ in range(30)]
# anywhere
incomes += [rng.randint(0, 10 ** 12) for _ in range(14)]

NEED = ("allowance_cents", "taxable_cents", "tax_before_credit_cents")
problems, judged = [], 0
for income in incomes:
    request = {"income_cents": income, "dependents": rng.randint(0, 20)}
    body, problem = taxed(request, needed=NEED)
    if problem:
        problems.append(problem)
        continue
    got_allowance = body["allowance_cents"]
    if (TAPER_FROM < income < TAPER_END and got_allowance != STANDARD_ALLOWANCE
            and got_allowance in allowance_either_rounding(income)):
        judged += 1
        if got_allowance != allowance(income):
            problems.append(f"{request}: the reduction rounds up, so the allowance is {allowance(income)}, "
                            f"got {got_allowance}")
    got_taxable = body["taxable_cents"]
    exact = band_hundredths(got_taxable)
    if near_band_tax(body["tax_before_credit_cents"], exact):
        judged += 1
        if body["tax_before_credit_cents"] != half_up(exact):
            problems.append(f"{request}: on taxable {got_taxable} the tax before credit rounds half up to "
                            f"{half_up(exact)}, got {body['tax_before_credit_cents']}")

finish(problems, f"rounding ok: {judged} roundings judged on {len(incomes)} generated filers")
