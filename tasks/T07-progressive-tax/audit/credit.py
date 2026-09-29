"""X5 (G3): the dependents' credit. Each dependent is worth 450.00 off the tax before credit;
the credit cannot take the tax below zero, the unused part is lost, and the credit reported
is the part used. Checked against the reported tax before credit, so band errors do not
count here."""

import random

from _cmd import finish
from _model import CREDIT_PER_DEPENDENT, expected, table_error, taxed

# (income, dependents, tax before credit, credit used, tax owed), by hand, in cents
TABLE = [
    (2_100_000, 0, 45_000, 0, 45_000),
    (2_100_000, 1, 45_000, 45_000, 0),           # the credit exactly absorbs the tax
    (2_100_000, 2, 45_000, 45_000, 0),           # half the credit is lost
    (2_100_020, 1, 45_001, 45_000, 1),
    (4_000_000, 3, 320_000, 135_000, 185_000),
    (4_000_000, 7, 320_000, 315_000, 5_000),
    (4_000_000, 8, 320_000, 320_000, 0),
    (4_000_000, 20, 320_000, 320_000, 0),
    (6_000_000, 13, 700_000, 585_000, 115_000),
    (6_000_000, 15, 700_000, 675_000, 25_000),
    (6_000_000, 16, 700_000, 700_000, 0),
    (1_000_000, 5, 0, 0, 0),                     # no tax: no credit used
    (0, 20, 0, 0, 0),
    (100_000_000, 20, 36_200_000, 900_000, 35_300_000),
]

problems = []
for income, deps, before, used, owed in TABLE:
    model = expected(income, deps)
    if (model["tax_before_credit_cents"], model["credit_cents"], model["tax_cents"]) != (before, used, owed):
        table_error(problems, f"row {income}/{deps}: model gives {model}")

rng = random.Random(3_086_452)
cases = [(income, deps) for income, deps, *_ in TABLE]
cases += [(rng.randint(1_200_000, 8_000_000), rng.randint(0, 20)) for _ in range(60)]
cases += [(rng.randint(8_000_001, 400_000_000), rng.randint(0, 20)) for _ in range(12)]

for income, deps in cases:
    request = {"income_cents": income, "dependents": deps}
    body, problem = taxed(request, needed=("tax_before_credit_cents", "credit_cents", "tax_cents"))
    if problem:
        problems.append(problem)
        continue
    before = body["tax_before_credit_cents"]
    used = min(CREDIT_PER_DEPENDENT * deps, max(before, 0))
    if body["credit_cents"] != used or body["tax_cents"] != before - used:
        problems.append(f"{request}: with tax before credit {before}, expected credit {used} and tax "
                        f"{before - used}, got credit {body['credit_cents']} and tax {body['tax_cents']}")

finish(problems, f"credit ok: {len(cases)} filers")
