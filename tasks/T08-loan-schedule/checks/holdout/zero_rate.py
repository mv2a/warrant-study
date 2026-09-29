"""H5: interest-free loans charge no interest and pay the amount divided by the months, rounded up (G4)."""

import random

from _cmd import call, finish
from _model import MAX_MONTHS, MAX_PRINCIPAL, is_schedule

rng = random.Random(8085)
cases = [
    (1, 1), (1, MAX_MONTHS), (MAX_MONTHS, MAX_MONTHS), (MAX_MONTHS + 1, MAX_MONTHS), (MAX_PRINCIPAL, MAX_MONTHS),
    (MAX_PRINCIPAL, 1), (MAX_PRINCIPAL, 7), (100000, 7), (100000, 8), (50, 12), (11, 12), (12, 12), (13, 12),
    (999999999, 480), (100, 3),
]
cases += [(rng.randint(1, 500), rng.randint(1, MAX_MONTHS)) for _ in range(20)]
cases += [(rng.randrange(1200, 6000001, 1200), rng.choice((12, 24, 36, 48, 60))) for _ in range(10)]
cases += [(rng.randint(1, MAX_PRINCIPAL), rng.randint(1, MAX_MONTHS)) for _ in range(35)]

problems = []
for principal, months in cases:
    name = f"{principal} cents at 0 bp for {months} months"
    expected = -(-principal // months)
    status, body = call({"principal_cents": principal, "annual_rate_bp": 0, "months": months})
    if status != 0 or not is_schedule(body):
        problems.append(f"{name}: expected a schedule, got status {status}")
        continue
    if body.get("payment_cents") != expected:
        problems.append(f"{name}: expected a regular payment of {expected}, got {body.get('payment_cents')!r}")
        continue
    charged = [(row.get("month"), row.get("interest_cents")) for row in body["rows"] if row.get("interest_cents") != 0]
    if charged:
        month, amount = charged[0]
        problems.append(f"{name}: expected no interest in any month, got {amount!r} in month {month!r}")

finish(problems, f"interest-free loans ok: {len(cases)} loans")
