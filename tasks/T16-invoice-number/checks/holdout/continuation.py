"""H2: within the same year the sequence goes up by exactly one."""

import random

from _cmd import call, finish

PREFIXES = {"lisbon": "LIS", "porto": "OPO", "faro": "FAO", "braga": "BRG"}
EDGES = [1, 9, 10, 40, 99, 100, 999, 1000, 9999, 10000, 12340, 90000, 99998]
rng = random.Random(1602)
cases = []
for index, sequence in enumerate(EDGES):
    branch = sorted(PREFIXES)[index % 4]
    cases.append((branch, 2026, sequence))
for branch in PREFIXES:
    cases.append((branch, 2000, 1))
    cases.append((branch, 9999, 4750))
for _ in range(150):
    sequence = rng.choice((rng.randint(1, 99), rng.randint(1, 99998), rng.randint(1, 9999) * 10))
    cases.append((rng.choice(sorted(PREFIXES)), rng.randint(2000, 9999), min(sequence, 99998)))

problems = []
for branch, year, sequence in cases:
    request = {"branch": branch, "year": year, "previous": f"{PREFIXES[branch]}-{year}-{sequence:05d}"}
    status, body = call(request)
    got = body.get("sequence") if isinstance(body, dict) else None
    number = body.get("number") if isinstance(body, dict) else None
    tail = number.rsplit("-", 1)[-1] if isinstance(number, str) else ""
    if status != 0 or got != sequence + 1 or not tail.isdigit() or int(tail) != sequence + 1:
        problems.append(f"{request['previous']} in {year}: expected sequence {sequence + 1}, got {body!r} (status {status})")

finish(problems, f"continuation ok: {len(cases)} requests")
