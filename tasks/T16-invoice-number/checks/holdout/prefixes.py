"""H1: each branch numbers its invoices with its own prefix."""

import random

from _cmd import call, finish

PREFIXES = {"lisbon": "LIS", "porto": "OPO", "faro": "FAO", "braga": "BRG"}
rng = random.Random(1601)
cases = []
for branch, prefix in PREFIXES.items():
    for year in (2000, 2026, 9999):
        cases.append((branch, {"branch": branch, "year": year, "previous": None}))
        cases.append((branch, {"branch": branch, "year": year, "previous": f"{prefix}-{year}-00001"}))
    cases.append((branch, {"branch": branch, "year": 2027, "previous": f"{prefix}-2026-00815"}))
while len(cases) < 120:
    branch = rng.choice(sorted(PREFIXES))
    year = rng.randint(2000, 9999)
    kind = rng.choice(("first", "same", "earlier"))
    if kind == "first":
        previous = None
    elif kind == "same":
        previous = f"{PREFIXES[branch]}-{year}-{rng.randint(1, 99998):05d}"
    else:
        if year == 2000:
            continue
        previous = f"{PREFIXES[branch]}-{year - 1}-{rng.randint(1, 99999):05d}"
    cases.append((branch, {"branch": branch, "year": year, "previous": previous}))

problems = []
for branch, request in cases:
    status, body = call(request)
    number = body.get("number") if isinstance(body, dict) else None
    shown = number.split("-")[0] if isinstance(number, str) else None
    if status != 0 or shown != PREFIXES[branch]:
        problems.append(f"{request}: expected a number starting {PREFIXES[branch]}-, got {body!r} (status {status})")

finish(problems, f"prefixes ok: {len(cases)} requests")
