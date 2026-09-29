"""H2: books and DVDs forgive 3 late days and charge only the days after; reference items forgive none (G2)."""

import random

from _cmd import call, finish
from _model import RATE, fines_by_id, item

rng = random.Random(41700)
problems = []
cases = []
for kind in ("book", "dvd"):
    for late in range(0, 11):
        cases.append((kind, late, max(0, late - 3) * RATE[kind]))
for late in range(0, 11):
    cases.append(("reference", late, late * RATE["reference"]))
for _ in range(30):
    kind = rng.choice(("book", "dvd", "reference"))
    late = rng.randint(0, 9)
    grace = 0 if kind == "reference" else 3
    cases.append((kind, late, max(0, late - grace) * RATE[kind]))

for kind, late, expected in cases:
    due = rng.choice((0, 1, rng.randint(2, 400), rng.randint(10_000, 99_999)))
    status, body = call({"items": [item("g", kind, due, late)]})
    got = (fines_by_id(body) or {}).get("g") if status == 0 else None
    if got != expected:
        problems.append(f"{kind} due day {due}, {late} days late: expected {expected} cents, got {got!r} (status {status})")

finish(problems, f"grace ok: {len(cases)} items")
