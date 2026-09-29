"""X2 (G1): the bands at and around every edge. Each row's taxable income is a whole
multiple of 1.00, so the exact band tax is a whole number of cents and no rounding is
involved. The tax before credit must equal the band tax on the reported taxable income,
whatever the number of dependents. A reported taxable income below zero has no part inside
any band, so its band tax is zero (whether taxable income may be negative is C2's business)."""

from _cmd import finish
from _model import band_hundredths, either_cent, expected, table_error, taxed

# (income, dependents, taxable by hand, tax before credit by hand), all in cents
ROWS = [
    (0, 0, 0, 0),
    (1_150_000, 2, 0, 0),                       # income below the allowance
    (1_200_000, 0, 0, 0),
    (1_200_100, 0, 100, 5),                     # 5% of 1.00
    (1_700_000, 1, 500_000, 25_000),            # 5% of 5,000.00
    (2_200_000, 0, 1_000_000, 50_000),          # first band full
    (2_200_000, 9, 1_000_000, 50_000),
    (2_200_100, 0, 1_000_100, 50_015),          # 15% starts above 10,000.00
    (3_200_000, 3, 2_000_000, 200_000),
    (5_200_000, 0, 4_000_000, 500_000),         # second band full
    (5_200_100, 0, 4_000_100, 500_025),         # 25% starts above 40,000.00
    (6_700_000, 5, 5_500_000, 875_000),
    (8_000_000, 0, 6_800_000, 1_200_000),
    (10_666_666, 0, 10_000_000, 2_000_000),     # third band full (tapered allowance 6,666.66)
    (10_666_750, 2, 10_000_100, 2_000_038),     # 38% starts above 100,000.00
    (14_000_000, 0, 14_000_000, 3_520_000),
    (14_000_100, 1, 14_000_100, 3_520_038),
    (25_000_000, 0, 25_000_000, 7_700_000),
    (123_456_700, 4, 123_456_700, 45_113_546),
    (1_000_000_000_000, 0, 1_000_000_000_000, 379_998_200_000),
]

problems = []
for income, deps, hand_taxable, hand_before in ROWS:
    model = expected(income, deps)
    if (model["taxable_cents"], model["tax_before_credit_cents"]) != (hand_taxable, hand_before):
        table_error(problems, f"row {income}: model gives {model}")
        continue
    request = {"income_cents": income, "dependents": deps}
    body, problem = taxed(request, needed=("taxable_cents", "tax_before_credit_cents"))
    if problem:
        problems.append(problem)
        continue
    taxable = body["taxable_cents"]
    allowed = either_cent(band_hundredths(taxable))
    if body["tax_before_credit_cents"] not in allowed:
        problems.append(f"{request}: taxable {taxable} gives tax before credit "
                        f"{sorted(allowed)} by the bands, got {body['tax_before_credit_cents']}"
                        f" (for taxable {hand_taxable} the intent gives {hand_before})")

finish(problems, f"band edges ok: {len(ROWS)} filers")
