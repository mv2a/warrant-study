"""X6 (C1): rounding at the edges. The tax before credit is the exact band tax rounded to the
nearest cent with an exact half cent rounded UP (not to even, not down, not truncated),
including for incomes far beyond floating-point precision; a fractional allowance
reduction is rounded UP to the next whole cent.

Only the rounding is judged here. A tax before credit more than a cent away from the exact
band tax on the reported taxable income (beyond one part in 10**14 for amounts far past
ordinary incomes) is a band error, G1's business; an allowance outside the two whole cents
around the exact G2 allowance, or the full 12,000.00 above 80,000.00 of income (no phase-out
applied at all), is a phase-out error, G2's business. Neither is judged here."""

from _cmd import finish
from _model import (STANDARD_ALLOWANCE, allowance_either_rounding, band_hundredths, expected, half_up,
                    near_band_tax, table_error, taxed)

# (income, allowance by hand or None when no rounding is involved, taxable, tax before credit)
ROWS = [
    (1_200_009, None, 9, 0),                     # 0.45 cent
    (1_200_010, None, 10, 1),                    # 0.5 cent rounds up
    (1_200_011, None, 11, 1),                    # 0.55 cent
    (1_200_029, None, 29, 1),                    # 1.45 cents
    (1_200_050, None, 50, 3),                    # 2.5 cents rounds up (not to even)
    (1_200_090, None, 90, 5),                    # 4.5 cents
    (1_210_010, None, 10_010, 501),              # 500.5 cents
    (2_200_003, None, 1_000_003, 50_000),        # 50,000.45
    (2_200_010, None, 1_000_010, 50_002),        # 50,001.5
    (2_200_030, None, 1_000_030, 50_005),        # 50,004.5
    (3_333_350, None, 2_133_350, 220_003),       # 220,002.5
    (5_200_001, None, 4_000_001, 500_000),       # 500,000.25
    (5_200_002, None, 4_000_002, 500_001),       # 500,000.5
    (5_200_003, None, 4_000_003, 500_001),       # 500,000.75
    (7_654_322, None, 6_454_322, 1_113_581),     # 1,113,580.5
    (14_000_001, None, 14_000_001, 3_520_000),   # 3,520,000.38
    (14_000_002, None, 14_000_002, 3_520_001),   # 3,520,000.76
    (14_000_025, None, 14_000_025, 3_520_010),   # 3,520,009.5
    (14_000_075, None, 14_000_075, 3_520_029),   # 3,520,028.5
    (50_000_075, None, 50_000_075, 17_200_029),  # 17,200,028.5
    (9_007_199_254_740_993, None, 9_007_199_254_740_993, 3_422_735_715_001_577),     # 2**53 + 1
    (10 ** 18 + 10_000_075, None, 10 ** 18 + 10_000_075, 380_000_000_002_000_029),  # ...028.5
    (987_654_321_987_654_321, None, 987_654_321_987_654_321, 375_308_642_353_508_642),
    # allowance reduction rounded up: (income - 80,000.00) / 5 is not a whole cent
    (8_000_001, 1_199_999, 6_800_002, 1_200_001),     # reduction 0.2 -> 1; tax 1,200,000.5
    (8_000_004, 1_199_999, 6_800_005, 1_200_001),     # 0.8 -> 1; tax 1,200,001.25
    (8_000_005, 1_199_999, 6_800_006, 1_200_002),     # 1 exactly; tax 1,200,001.5
    (8_000_006, 1_199_998, 6_800_008, 1_200_002),     # 1.2 -> 2
    (9_876_543, 824_691, 9_051_852, 1_762_963),       # 375,308.6 -> 375,309
    (10_666_667, 666_666, 10_000_001, 2_000_000),     # 533,333.4 -> 533,334
    (12_345_678, 330_864, 12_014_814, 2_765_629),     # 869,135.6 -> 869,136
    (13_999_995, 1, 13_999_994, 3_519_998),           # 1,199,999 exactly
    (13_999_996, 0, 13_999_996, 3_519_998),           # 1,199,999.2 -> 1,200,000
    (13_999_999, 0, 13_999_999, 3_520_000),           # 1,199,999.8 -> 1,200,000
]

NEED = ("allowance_cents", "taxable_cents", "tax_before_credit_cents")
problems = []
for income, allow, taxable, before in ROWS:
    model = expected(income, 0)
    if ((allow is not None and model["allowance_cents"] != allow)
            or (model["taxable_cents"], model["tax_before_credit_cents"]) != (taxable, before)):
        table_error(problems, f"row {income}: model gives {model}")

judged = 0
for income, allow, taxable, before in ROWS:
    request = {"income_cents": income, "dependents": 0}
    body, problem = taxed(request, needed=NEED)
    if problem:
        problems.append(problem)
        continue
    got_allowance = body["allowance_cents"]
    if (allow is not None and got_allowance != STANDARD_ALLOWANCE
            and got_allowance in allowance_either_rounding(income)):
        judged += 1
        if got_allowance != allow:
            problems.append(f"{request}: the reduction rounds up, so the allowance is {allow}, "
                            f"got {got_allowance}")
    got_taxable = body["taxable_cents"]
    exact = band_hundredths(got_taxable)
    if near_band_tax(body["tax_before_credit_cents"], exact):
        judged += 1
        if body["tax_before_credit_cents"] != half_up(exact):
            problems.append(f"{request}: on taxable {got_taxable} the tax before credit rounds to "
                            f"{half_up(exact)}, got {body['tax_before_credit_cents']} "
                            f"(intent: {before} on {taxable})")

finish(problems, f"rounding edges ok: {judged} roundings judged on {len(ROWS)} filers")
