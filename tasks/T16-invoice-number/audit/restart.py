"""X5 (G3): the sequence is 1 when previous is null, and when a well-formed previous
number is from any earlier year: one year earlier, thousands of years earlier, and even
when that earlier sequence reached 99999; plus generated cases (seed 16_5881)."""

import random

from _x import BRANCHES, PREFIX, encode, finish, invoke_all, parse, show

FIXED = [  # (branch, request year, previous year or None, previous sequence)
    ("lisbon", 2000, None, 0), ("porto", 2001, None, 0), ("faro", 5555, None, 0), ("braga", 9999, None, 0),
    ("lisbon", 2001, 2000, 1), ("porto", 2001, 2000, 99999), ("faro", 9999, 9998, 12),
    ("braga", 9999, 2000, 2), ("lisbon", 9999, 2000, 99999), ("porto", 2040, 2039, 99999),
    ("faro", 2040, 2039, 1), ("braga", 2040, 2039, 99998), ("lisbon", 3000, 2999, 40000),
    ("porto", 2100, 2099, 60606), ("faro", 2046, 2012, 700), ("braga", 6300, 6299, 99999),
]

rng = random.Random(16_5881)
GENERATED = []
for i in range(120):
    branch = rng.choice(BRANCHES)
    year = rng.randint(2000, 9999)
    if i % 5 == 0 or year == 2000:
        GENERATED.append((branch, year, None, 0))
        continue
    gap = rng.choice([1, 1, 2, rng.randint(1, year - 2000)])
    GENERATED.append((branch, year, year - min(gap, year - 2000), rng.randint(1, 99999)))

cases = FIXED + GENERATED
requests = [
    {"branch": b, "year": y, "previous": None if py is None else f"{PREFIX[b]}-{py:04d}-{s:05d}"}
    for b, y, py, s in cases
]

problems = []
results = invoke_all([encode(r) for r in requests])
for request, (status, out) in zip(requests, results):
    body = parse(out) or {}
    number, sequence = body.get("number"), body.get("sequence")
    tail = number.rsplit("-", 1)[-1] if isinstance(number, str) else ""
    shown = int(tail) if tail.isascii() and tail.isdigit() else None
    if status != 0:
        problems.append(f"{show(request)}: status {status}, expected 0 and sequence 1")
    elif sequence != 1 or isinstance(sequence, bool) or shown != 1:
        problems.append(f"{show(request)}: expected sequence 1, got number {show(number)} sequence {show(sequence)}")

finish(problems, f"restart ok: {len(cases)} requests ({len(FIXED)} fixed, {len(GENERATED)} generated)")
