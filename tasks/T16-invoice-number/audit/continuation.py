"""X4 (G2): a well-formed previous number from the request's own year is continued by
exactly one, both in the response's sequence and in the number's final part: at every
digit-width boundary, at the years 2000 and 9999, and in generated cases (seed 16_2917)."""

import random

from _x import BRANCHES, PREFIX, encode, finish, invoke_all, parse, show

FIXED = [  # (branch, year, previous sequence)
    ("lisbon", 2031, 1), ("porto", 2031, 2), ("faro", 2031, 9), ("braga", 2031, 10),
    ("lisbon", 2032, 99), ("porto", 2032, 100), ("faro", 2032, 998), ("braga", 2032, 999),
    ("lisbon", 2033, 1000), ("porto", 2033, 9999), ("faro", 2033, 10000), ("braga", 2033, 54320),
    ("lisbon", 2034, 99997), ("porto", 2034, 99998), ("faro", 2034, 99998), ("braga", 2034, 99998),
    ("lisbon", 2000, 1), ("porto", 2000, 4507), ("faro", 9999, 1), ("braga", 9999, 88888),
    ("lisbon", 2099, 19), ("porto", 2100, 190), ("faro", 7007, 1899), ("braga", 8080, 29999),
]

rng = random.Random(16_2917)
GENERATED = []
for _ in range(160):
    branch = rng.choice(BRANCHES)
    year = rng.randint(2000, 9999)
    width = rng.randint(1, 5)  # spread the sequences over every digit width
    seq = rng.randint(10 ** (width - 1), min(10 ** width - 1, 99998))
    GENERATED.append((branch, year, seq))

cases = FIXED + GENERATED
requests = [{"branch": b, "year": y, "previous": f"{PREFIX[b]}-{y:04d}-{s:05d}"} for b, y, s in cases]

problems = []
results = invoke_all([encode(r) for r in requests])
for (branch, year, seq), request, (status, out) in zip(cases, requests, results):
    body = parse(out) or {}
    number, sequence = body.get("number"), body.get("sequence")
    tail = number.rsplit("-", 1)[-1] if isinstance(number, str) else ""
    shown = int(tail) if tail.isascii() and tail.isdigit() else None
    if status != 0:
        problems.append(f"{show(request)}: status {status}, expected 0 and sequence {seq + 1}")
    elif sequence != seq + 1 or isinstance(sequence, bool) or shown != seq + 1:
        problems.append(f"{show(request)}: expected sequence {seq + 1}, got number {show(number)} sequence {show(sequence)}")

finish(problems, f"continuation ok: {len(cases)} requests ({len(FIXED)} fixed, {len(GENERATED)} generated)")
