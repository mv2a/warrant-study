"""X6 (C1): the number is exactly PREFIX-YYYY-NNNNN with the request's year in four digits
and the sequence zero-padded to exactly five digits, and the response's sequence is that
same value as a JSON whole number: every padding width, restarts that must carry the
request's year rather than the previous one's, and generated cases (seed 16_4402)."""

import random

from _x import BRANCHES, PREFIX, encode, finish, invoke_all, parse, show

# (branch, request year, previous or None, expected sequence)
FIXED = [
    ("lisbon", 2071, None, 1),
    ("porto", 2071, "OPO-2071-00009", 10),
    ("faro", 2071, "FAO-2071-00099", 100),
    ("braga", 2071, "BRG-2071-00999", 1000),
    ("lisbon", 2071, "LIS-2071-09999", 10000),
    ("porto", 2071, "OPO-2071-99998", 99999),
    ("faro", 2071, "FAO-2071-12344", 12345),
    ("braga", 2071, "BRG-2071-00100", 101),
    ("lisbon", 2000, "LIS-2000-00020", 21),
    ("porto", 9999, "OPO-9999-00300", 301),
    ("faro", 2072, "FAO-2071-04321", 1),
    ("braga", 9999, "BRG-2000-00077", 1),
    ("lisbon", 2010, "LIS-2009-99999", 1),
]

rng = random.Random(16_4402)
GENERATED = []
for _ in range(100):
    branch, year = rng.choice(BRANCHES), rng.randint(2000, 9999)
    kind = rng.choice(["new", "same", "same", "earlier"]) if year > 2000 else rng.choice(["new", "same"])
    if kind == "new":
        GENERATED.append((branch, year, None, 1))
    elif kind == "same":
        seq = rng.choice([rng.randint(1, 98), rng.randint(99, 9998), rng.randint(9999, 99998)])
        GENERATED.append((branch, year, f"{PREFIX[branch]}-{year}-{seq:05d}", seq + 1))
    else:
        earlier = rng.randint(2000, year - 1)
        GENERATED.append((branch, year, f"{PREFIX[branch]}-{earlier}-{rng.randint(1, 99999):05d}", 1))

cases = FIXED + GENERATED
problems = []
results = invoke_all([encode({"branch": b, "year": y, "previous": p}) for b, y, p, _ in cases])
for (branch, year, previous, seq), (status, out) in zip(cases, results):
    want = f"{PREFIX[branch]}-{year:04d}-{seq:05d}"
    body = parse(out) or {}
    label = f"{branch} {year} previous {previous!r}"
    if status != 0:
        problems.append(f"{label}: status {status}, expected 0 and {want}")
    elif body.get("number") != want:
        problems.append(f"{label}: expected number {want}, got {show(body.get('number'))}")
    elif type(body.get("sequence")) is not int or body["sequence"] != seq:
        problems.append(f"{label}: expected sequence {seq} as a whole number, got {show(body.get('sequence'))}")

finish(problems, f"format ok: {len(cases)} numbers ({len(FIXED)} fixed, {len(GENERATED)} generated)")
