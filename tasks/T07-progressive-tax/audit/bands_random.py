"""X3 (G1): generated filers (fixed seed) in every band, in the allowance taper and far
above it. The tax before credit must be the exact band tax on the reported taxable income,
rounded down or up to a whole cent (which way is C1's business, checked elsewhere). A
reported taxable income below zero has no part inside any band, so its band tax is zero
(whether taxable income may be negative is C2's business)."""

import random

from _cmd import finish
from _model import band_hundredths, either_cent, taxed

rng = random.Random(91_417_263)
RANGES = [  # (lowest income, highest income, how many)
    (0, 1_200_000, 8),                  # no taxable income
    (1_200_001, 2_200_000, 14),         # taxable income in the 5% band
    (2_200_001, 5_200_000, 14),         # 15% band
    (5_200_001, 8_000_000, 14),         # 25% band, standard allowance
    (8_000_001, 13_999_999, 24),        # allowance taper, 25% and 38% bands
    (14_000_000, 60_000_000, 16),       # no allowance, 38% band
    (60_000_001, 90_000_000_000, 12),
]

problems, count = [], 0
for low, high, n in RANGES:
    for _ in range(n):
        request = {"income_cents": rng.randint(low, high), "dependents": rng.randint(0, 20)}
        count += 1
        body, problem = taxed(request, needed=("taxable_cents", "tax_before_credit_cents"))
        if problem:
            problems.append(problem)
            continue
        taxable = body["taxable_cents"]
        allowed = either_cent(band_hundredths(taxable))
        if body["tax_before_credit_cents"] not in allowed:
            problems.append(f"{request}: taxable {taxable} gives tax before credit {sorted(allowed)} "
                            f"by the bands, got {body['tax_before_credit_cents']}")

finish(problems, f"bands ok: {count} generated filers")
