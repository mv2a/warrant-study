"""H6: numbering never goes backwards and never outgrows five digits."""

import random

from _cmd import call, finish

PREFIXES = {"lisbon": "LIS", "porto": "OPO", "faro": "FAO", "braga": "BRG"}
rng = random.Random(1606)
refused = []
for branch, prefix in PREFIXES.items():
    for year, previous_year in ((2026, 2027), (2026, 2028), (2026, 2126), (2000, 9999), (9998, 9999), (2000, 2001)):
        for sequence in (1, 41, 99999):
            refused.append({"branch": branch, "year": year, "previous": f"{prefix}-{previous_year}-{sequence:05d}"})
    for year in (2000, 2026, 9999):
        refused.append({"branch": branch, "year": year, "previous": f"{prefix}-{year}-99999"})
for _ in range(40):
    branch = rng.choice(sorted(PREFIXES))
    year = rng.randint(2000, 9998)
    previous_year = rng.choice((year + 1, rng.randint(year + 1, 9999)))
    refused.append({"branch": branch, "year": year, "previous": f"{PREFIXES[branch]}-{previous_year}-{rng.randint(1, 99999):05d}"})

accepted = []
for branch, prefix in PREFIXES.items():
    accepted.append(({"branch": branch, "year": 2026, "previous": f"{prefix}-2026-99998"}, 99999))
    accepted.append(({"branch": branch, "year": 2027, "previous": f"{prefix}-2026-99999"}, 1))
    accepted.append(({"branch": branch, "year": 9999, "previous": f"{prefix}-9999-00001"}, 2))

problems = []
for request in refused:
    status, body = call(request)
    if status != 2 or body is not None:
        problems.append(f"{request}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for request, expected in accepted:
    status, body = call(request)
    got = body.get("sequence") if isinstance(body, dict) else None
    if status != 0 or got != expected:
        problems.append(f"{request}: expected sequence {expected}, got {body!r} (status {status})")

finish(problems, f"order ok: {len(refused)} refused, {len(accepted)} accepted")
