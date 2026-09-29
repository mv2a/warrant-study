"""H9: 160 random requests of every kind, compared field by field with the whole intent."""

import random

from _cmd import call, finish
from _model import DAYS, quote, refused

rng = random.Random(20260929)
cases = []
for _ in range(160):
    day = rng.choice(DAYS)
    n = rng.choice([rng.randint(1, 3), rng.randint(1, 30), rng.randint(6, 15)])
    rate = rng.choice([rng.randint(1, 999), rng.randint(1000, 60000), rng.randint(60000, 2000000)])
    cases.append((day, n, rate))

problems = []
for day, n, rate in cases:
    status, body = call({"check_in": day, "nights": n, "rate_cents": rate})
    want = quote(day, n, rate)
    if want is None:
        if not refused(status, body):
            problems.append(f"{day}, {n} nights at {rate}: should be refused, got {body!r} (status {status})")
    elif status != 0 or body != want:
        problems.append(f"{day}, {n} nights at {rate}: expected {want}, got {body!r} (status {status})")

finish(problems, f"whole-intent model ok: {len(cases)} requests")
