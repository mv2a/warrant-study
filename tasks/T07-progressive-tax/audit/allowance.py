"""X4 (G2): the allowance. It is 12,000.00 up to an income of 80,000.00, shrinks by one fifth
of the income above 80,000.00, is zero from 140,000.00 and never goes below zero. Where the
fifth is a whole cent the allowance is exact; where it is not, rounding either way is
accepted here (C1 fixes the direction and is checked elsewhere)."""

import random

from _cmd import finish
from _model import allowance_either_rounding, table_error, taxed

# (income, dependents, allowed allowances by hand), in cents
TABLE = [
    (0, 0, {1_200_000}),
    (1, 3, {1_200_000}),
    (1_199_999, 0, {1_200_000}),
    (4_000_000, 1, {1_200_000}),
    (7_999_999, 0, {1_200_000}),
    (8_000_000, 2, {1_200_000}),                 # "above 80,000.00": no reduction yet
    (8_000_005, 0, {1_199_999}),                 # 0.05 over gives 0.01 less
    (8_000_010, 0, {1_199_998}),
    (8_500_000, 4, {1_100_000}),
    (9_000_000, 0, {1_000_000}),
    (11_000_000, 20, {600_000}),
    (12_500_000, 0, {300_000}),
    (13_999_995, 0, {1}),
    (14_000_000, 0, {0}),                        # zero at 140,000.00
    (14_000_005, 1, {0}),                        # never below zero
    (14_500_000, 0, {0}),
    (40_000_000, 6, {0}),
    (1_000_000_000_000, 0, {0}),
    (10 ** 18, 0, {0}),
    (8_000_001, 0, {1_200_000, 1_199_999}),      # fractional reductions
    (8_000_003, 0, {1_200_000, 1_199_999}),
    (10_000_002, 0, {800_000, 799_999}),
    (13_999_999, 0, {1, 0}),
    (14_000_001, 0, {0}),
]

rng = random.Random(5_530_881)
GENERATED = ([rng.randint(0, 8_000_000) for _ in range(8)]
             + [rng.randint(8_000_001, 13_999_999) for _ in range(36)]
             + [rng.randint(14_000_000, 10 ** 13) for _ in range(10)])

problems, count = [], 0
cases = [(income, deps, allowed) for income, deps, allowed in TABLE]
for income, deps, allowed in TABLE:
    if allowance_either_rounding(income) != allowed:
        table_error(problems, f"income {income}: model allows {allowance_either_rounding(income)}")
cases += [(income, rng.randint(0, 20), allowance_either_rounding(income)) for income in GENERATED]

for income, deps, allowed in cases:
    request = {"income_cents": income, "dependents": deps}
    count += 1
    body, problem = taxed(request, needed=("allowance_cents",))
    if problem:
        problems.append(problem)
    elif body["allowance_cents"] not in allowed:
        problems.append(f"{request}: allowance should be {' or '.join(map(str, sorted(allowed)))}, "
                        f"got {body['allowance_cents']}")

finish(problems, f"allowance ok: {count} filers")
