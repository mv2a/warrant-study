"""H3: numbering restarts at 1 every year and for a branch with no previous number."""

import random

from _cmd import call, finish

PREFIXES = {"lisbon": "LIS", "porto": "OPO", "faro": "FAO", "braga": "BRG"}
rng = random.Random(1603)
cases = []
for branch, prefix in PREFIXES.items():
    for year in (2000, 2001, 2026, 5000, 9999):
        cases.append({"branch": branch, "year": year, "previous": None})
    for gap in (1, 2, 3, 10, 100, 7999):
        for sequence in (1, 41, 99999):
            cases.append({"branch": branch, "year": 2000 + gap, "previous": f"{prefix}-2000-{sequence:05d}"})
    cases.append({"branch": branch, "year": 9999, "previous": f"{prefix}-9998-00300"})
for _ in range(60):
    branch = rng.choice(sorted(PREFIXES))
    year = rng.randint(2001, 9999)
    earlier = rng.choice((year - 1, rng.randint(2000, year - 1)))
    cases.append({"branch": branch, "year": year, "previous": f"{PREFIXES[branch]}-{earlier}-{rng.randint(1, 99999):05d}"})

problems = []
for request in cases:
    status, body = call(request)
    got = body.get("sequence") if isinstance(body, dict) else None
    number = body.get("number") if isinstance(body, dict) else None
    parts = number.split("-") if isinstance(number, str) else []
    ok = len(parts) == 3 and parts[1] == str(request["year"]) and parts[2].isdigit() and int(parts[2]) == 1
    if status != 0 or got != 1 or not ok:
        problems.append(f"{request}: expected sequence 1 in {request['year']}, got {body!r} (status {status})")

finish(problems, f"yearly reset ok: {len(cases)} requests")
