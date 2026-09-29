"""H8 (S1-S4): each scenario in intent.md, sent compact and pretty-printed, gets exactly the stated response."""

import json

from _cmd import call, finish

SCENARIOS = [
    ("S1", {"income_cents": 3000000, "dependents": 0},
     {"income_cents": 3000000, "allowance_cents": 1200000, "taxable_cents": 1800000,
      "tax_before_credit_cents": 170000, "credit_cents": 0, "tax_cents": 170000}),
    ("S2", {"income_cents": 9500000, "dependents": 2},
     {"income_cents": 9500000, "allowance_cents": 900000, "taxable_cents": 8600000,
      "tax_before_credit_cents": 1650000, "credit_cents": 90000, "tax_cents": 1560000}),
    ("S3", {"income_cents": 1400000, "dependents": 3},
     {"income_cents": 1400000, "allowance_cents": 1200000, "taxable_cents": 200000,
      "tax_before_credit_cents": 10000, "credit_cents": 10000, "tax_cents": 0}),
    ("S4", {"income_cents": 1200030, "dependents": 0},
     {"income_cents": 1200030, "allowance_cents": 1200000, "taxable_cents": 30,
      "tax_before_credit_cents": 2, "credit_cents": 0, "tax_cents": 2}),
]
problems = []
for name, request, expected in SCENARIOS:
    for raw in (json.dumps(request, separators=(",", ":")), json.dumps(dict(reversed(request.items())), indent=2)):
        status, body = call(raw=raw)
        if status != 0 or body != expected:
            problems.append(f"{name}: expected status 0 and {expected}, got status {status} and {body!r}")

finish(problems, f"scenarios ok: {len(SCENARIOS)} filers, 2 spellings each")
