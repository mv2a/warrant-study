"""X10 (C3): every request that is not invalid is taxed (exit status 0 and a JSON object
carrying a tax_cents figure): an income of zero, the smallest and largest numbers of
dependents (0 and 20), very large incomes, and extra fields of any kind, including ones that
look invalid. The exact shape of the response is C4's business, checked by X1."""

import json

from _cmd import finish
from _model import short, taxed

requests = [
    {"income_cents": 0, "dependents": 0},
    {"income_cents": 0, "dependents": 20},
    {"income_cents": 1, "dependents": 0},
    {"income_cents": 7_300_000, "dependents": 20},
    {"income_cents": 4_444_444, "dependents": 19},
    {"income_cents": 10 ** 20, "dependents": 20},
    {"income_cents": 10 ** 30, "dependents": 0},
    {"dependents": 20, "income_cents": 0},
    {"income_cents": 2_600_000, "dependents": 1, "income": -5, "extra": None, "dependents_note": 21.5},
    {"income_cents": 2_600_000, "dependents": 0, "credit_cents": "all", "children": [1, 2, 3]},
]
raws = ['\n\t{ "income_cents" : 4000000 ,\n  "dependents" : 2 }\n  ']

problems = []
for request, raw in [(r, None) for r in requests] + [(None, r) for r in raws]:
    body, problem = taxed(request, raw=raw, needed=())
    if problem is None and "tax_cents" not in body:
        problem = f"{short(raw if raw is not None else request)}: exit status 0 but no tax_cents in {short(body)}"
    if problem:
        problems.append(problem)

finish(problems, f"valid requests taxed: {len(requests) + len(raws)}")
