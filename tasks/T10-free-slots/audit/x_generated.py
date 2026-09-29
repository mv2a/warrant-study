"""X12 (G1, G2, G3, C1, C2, C3): generated requests get exactly the audit model's slots.

Unlike X5-X10, each answer here is compared exactly, in the order returned, so a fault in
any of the six promises shows up. Requests are unsorted, overlapping and nested at random,
with quorums from one person to the whole group.
"""

import random

from _cmd import call, finish
from _model import describe, expected, random_request, slots_of

rng = random.Random(9_000_917)
CASES = []
for n in range(160):
    options = {}
    if n % 4 == 1:
        options = {"grid": rng.choice([5, 10, 30]), "longest": 90}
    elif n % 4 == 2:
        options = {"people": rng.randint(6, 20), "per_person": rng.randint(1, 4), "longest": 45}
    elif n % 4 == 3:
        options = {"spill": 400, "longest": 400}
    CASES.append(random_request(rng, **options))

problems = []
for request in CASES:
    want = expected(request)
    status, body = call(request)
    got = slots_of(status, body)
    if got is None:
        problems.append(f"{describe(request)}: no usable answer (status {status}, {str(body)[:60]})")
    elif got != want:
        problems.append(f"{describe(request)}: expected {want[:5]}, got {got[:5]}")

finish(problems, f"generated ok: {len(CASES)} requests")
