"""H4: numbers are written PREFIX-YYYY-NNNNN and sequence matches the number."""

import random
import re

from _cmd import call, finish

PREFIXES = {"lisbon": "LIS", "porto": "OPO", "faro": "FAO", "braga": "BRG"}
SHAPE = re.compile(r"[A-Z]{3}-[0-9]{4}-[0-9]{5}")
rng = random.Random(1604)
cases = []
for sequence in (0, 8, 9, 98, 99, 998, 999, 9998, 9999, 99998):
    cases.append(("lisbon", 2026, f"LIS-2026-{sequence:05d}" if sequence else None, sequence + 1))
while len(cases) < 200:
    branch = rng.choice(sorted(PREFIXES))
    year = rng.randint(2000, 9999)
    digits = rng.randint(1, 5)
    sequence = rng.randint(10 ** (digits - 1), min(10**digits - 1, 99998))
    kind = rng.random()
    if kind < 0.15:
        cases.append((branch, year, None, 1))
    elif kind < 0.3 and year > 2000:
        cases.append((branch, year, f"{PREFIXES[branch]}-{year - 1}-{sequence:05d}", 1))
    else:
        cases.append((branch, year, f"{PREFIXES[branch]}-{year}-{sequence:05d}", sequence + 1))

problems = []
for branch, year, previous, _ in cases:
    request = {"branch": branch, "year": year, "previous": previous}
    status, body = call(request)
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{request}: expected an answer, got {body!r} (status {status})")
        continue
    number, sequence = body.get("number"), body.get("sequence")
    if not isinstance(number, str) or not SHAPE.fullmatch(number):
        problems.append(f"{request}: number {number!r} is not PREFIX-YYYY-NNNNN")
    elif type(sequence) is not int or not 1 <= sequence <= 99999:
        problems.append(f"{request}: sequence {sequence!r} is not a whole number from 1 to 99999")
    elif number != f"{PREFIXES[branch]}-{year}-{sequence:05d}":
        problems.append(f"{request}: expected number {PREFIXES[branch]}-{year}-{sequence:05d} for sequence {sequence}, got {number!r}")

finish(problems, f"format ok: {len(cases)} requests")
