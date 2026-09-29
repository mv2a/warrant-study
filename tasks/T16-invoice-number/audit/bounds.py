"""X10 (C3): numbering never goes backwards or past five digits. A well-formed previous
number from a later year than the request (one year later up to 7999 years later, any
sequence) is refused with status 2, and so is sequence 99999 from the request's own
year, for all four branches; plus generated later-year cases (seed 16_3091)."""

import random

from _x import BRANCHES, PREFIX, encode, expect_refusals, finish

FIXED = [  # (branch, request year, previous year, previous sequence)
    ("lisbon", 2052, 2053, 1), ("porto", 2052, 2053, 50000), ("faro", 2052, 2053, 99998),
    ("braga", 2052, 2053, 99999), ("lisbon", 2000, 2001, 1), ("porto", 2000, 9999, 1),
    ("faro", 9998, 9999, 12), ("braga", 2000, 9999, 99999), ("lisbon", 2099, 2100, 3),
    ("porto", 4999, 5000, 777), ("faro", 2070, 2170, 40), ("braga", 2400, 2401, 1),
]
for branch in BRANCHES:  # the same year at 99999: the next number would need six digits
    for year in (2000, 2066, 6021, 9999):
        FIXED.append((branch, year, year, 99999))

rng = random.Random(16_3091)
GENERATED = []
for _ in range(90):
    year = rng.randint(2000, 9998)
    later = year + rng.choice([1, 1, 2, rng.randint(1, 9999 - year)])
    GENERATED.append((rng.choice(BRANCHES), year, min(later, 9999), rng.randint(1, 99999)))

cases = []
for branch, year, dated, seq in FIXED + GENERATED:
    request = {"branch": branch, "year": year, "previous": f"{PREFIX[branch]}-{dated}-{seq:05d}"}
    why = "later year" if dated > year else "sequence 99999 in the same year"
    cases.append((f"{branch} {year} previous {request['previous']} ({why})", encode(request)))

problems = []
n = expect_refusals(problems, cases, "numbering may not go backwards or past 99999")
finish(problems, f"bounds ok: {n} requests refused ({len(FIXED)} fixed, {len(GENERATED)} generated)")
