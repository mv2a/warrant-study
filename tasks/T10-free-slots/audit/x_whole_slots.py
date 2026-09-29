"""X7 (G3): every free stretch comes back whole, slots never overlap or touch, earliest first.

Answers are compared exactly, in the order returned, with the audit's own model, and
generated answers are also checked for order, gaps between slots and maximal edges.
"""

import random

from _cmd import call, finish
from _model import all_of, describe, expected, random_busy, random_quorum, random_workday, slots_of

W = [540, 1020]
CASES = [
    # A long stretch is one slot, not pieces of min_length.
    ({"workday": W, "min_length": 30, "busy": [[[540, 600]], [[900, 960]]]}, [[600, 900], [960, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[]]}, [[540, 1020]]),
    ({"workday": W, "min_length": 15, "busy": [[]]}, [[540, 1020]]),
    ({"workday": [0, 1440], "min_length": 60, "busy": [[[700, 740]]]}, [[0, 700], [740, 1440]]),
    # A free stretch is not cut where one person's free time ends and another's begins.
    ({"workday": W, "min_length": 30, "busy": [[[540, 600], [800, 1020]], [[540, 560], [700, 1020]]]}, [[600, 700]]),
    ({"workday": W, "min_length": 30, "busy": [[[540, 650]], [[540, 600]], [[540, 620]]]}, [[650, 1020]]),
    # Two people with the very same free time give one slot, not two copies.
    ({"workday": W, "min_length": 30, "busy": [[[600, 900]], [[600, 900]]]}, [[540, 600], [900, 1020]]),
    # Meetings from different people that touch or overlap leave slots that don't touch.
    ({"workday": W, "min_length": 1, "busy": [[[600, 650]], [[650, 700]], [[690, 760]]]}, [[540, 600], [760, 1020]]),
    # Busy intervals listed latest first still give slots earliest first.
    ({"workday": W, "min_length": 20, "busy": [[[960, 990], [800, 830], [620, 640]], [[700, 710]]]},
     [[540, 620], [640, 700], [710, 800], [830, 960], [990, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[1000, 1010]], [[900, 910]], [[800, 810]], [[700, 710]], [[600, 610]]]},
     [[540, 600], [610, 700], [710, 800], [810, 900], [910, 1000], [1010, 1020]]),
    # Under a quorum below the whole group, a stretch stays one slot while the people who are
    # free change inside it.
    ({"workday": W, "min_length": 30, "quorum": 2, "busy": [[[560, 600], [700, 740]], [[600, 650]], [[650, 700]]]}, [[540, 1020]]),
    ({"workday": W, "min_length": 30, "quorum": 3, "busy": [[[560, 600], [700, 740]], [[600, 650]], [[650, 700]]]}, [[740, 1020]]),
    ({"workday": W, "min_length": 1, "quorum": 1, "busy": [[[600, 700]], [[650, 760]]]}, [[540, 650], [700, 1020]]),
    ({"workday": W, "min_length": 45, "quorum": 3, "busy": [[[550, 580], [610, 640]], [[570, 620], [900, 990]], [], [[960, 1000]], [[700, 720]]]},
     [[540, 1020]]),
    ({"workday": W, "min_length": 45, "quorum": 4, "busy": [[[550, 580], [610, 640]], [[570, 620], [900, 990]], [], [[960, 1000]], [[700, 720]]]},
     [[620, 960]]),
    # Quorum slots listed earliest first, from meetings listed latest first.
    ({"workday": W, "min_length": 10, "quorum": 2, "busy": [[[980, 1000], [800, 900], [580, 640]], [[990, 1020], [850, 870], [600, 610]], [[990, 995]]]},
     [[540, 600], [610, 850], [870, 990], [1000, 1020]]),
]
CASES = [(all_of(request), want) for request, want in CASES]

rng = random.Random(88_1357)
for _ in range(80):
    workday = random_workday(rng)
    busy = random_busy(rng, workday, grid=rng.choice([1, 1, 5, 30]), spill=45, longest=100)
    need = rng.choice([1, 1, 2, rng.randint(1, 45)])
    CASES.append(({"workday": workday, "min_length": need, "quorum": random_quorum(rng, busy), "busy": busy}, None))

problems = []
for request, want in CASES:
    if want is None:
        want = expected(request)
    status, body = call(request)
    got = slots_of(status, body)
    if got is None:
        problems.append(f"{describe(request)}: no usable answer (status {status}, {str(body)[:60]})")
        continue
    if got != want:
        problems.append(f"{describe(request)}: expected {want[:5]}, got {got[:5]}")
        continue
    for a, b in zip(got, got[1:]):
        if not a[1] < b[0]:
            problems.append(f"{describe(request)}: slots {a} and {b} overlap, touch or are out of order")

finish(problems, f"whole-slots ok: {len(CASES)} requests")
