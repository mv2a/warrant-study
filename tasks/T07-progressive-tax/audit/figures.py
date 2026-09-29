"""X8 (C2): the figures add up. For generated filers (fixed seed) and extreme incomes, the
response repeats the income, the taxable income is the income minus the reported allowance
(or zero when the allowance is larger), and the tax owed is the tax before credit minus the
credit used."""

import random

from _cmd import finish
from _model import taxed

rng = random.Random(6_184_027)
cases = [(0, 0), (1, 1), (1_199_999, 0), (1_200_000, 2), (1_200_001, 0), (8_000_000, 20),
         (13_999_996, 1), (10 ** 18, 3), (10 ** 25 + 7, 0)]
for _ in range(80):
    digits = rng.randint(1, 15)
    cases.append((rng.randint(0, 10 ** digits), rng.randint(0, 20)))

problems = []
for income, deps in cases:
    request = {"income_cents": income, "dependents": deps}
    body, problem = taxed(request)
    if problem:
        problems.append(problem)
        continue
    if body["income_cents"] != income:
        problems.append(f"{request}: income_cents must repeat the request, got {body['income_cents']}")
    taxable = max(0, income - body["allowance_cents"])
    if body["taxable_cents"] != taxable:
        problems.append(f"{request}: with allowance {body['allowance_cents']} the taxable income is "
                        f"{taxable}, got {body['taxable_cents']}")
    owed = body["tax_before_credit_cents"] - body["credit_cents"]
    if body["tax_cents"] != owed:
        problems.append(f"{request}: tax before credit {body['tax_before_credit_cents']} minus credit "
                        f"{body['credit_cents']} is {owed}, got tax {body['tax_cents']}")

finish(problems, f"figures add up: {len(cases)} filers")
