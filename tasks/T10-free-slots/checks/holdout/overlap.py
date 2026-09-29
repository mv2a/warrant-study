"""H5 (C2): overlapping, nested, repeated and shuffled intervals count as the time they cover together."""

import copy
import random

from _cmd import finish
from _oracle import compare, expected_slots, random_request

problems = []
cases = 0

DAY = [540, 1020]
FIXED = [
    ("a meeting inside another", [[[600, 720], [630, 660], [800, 900]]], [[540, 600], [720, 800], [900, 1020]]),
    ("a meeting inside another person's", [[[600, 720], [800, 900]], [[630, 660]]], [[540, 600], [720, 800], [900, 1020]]),
    ("several meetings inside one", [[[600, 900], [610, 620], [700, 800], [850, 899]]], [[540, 600], [900, 1020]]),
    ("the same start, different ends", [[[600, 700], [600, 640]], [[600, 660]]], [[540, 600], [700, 1020]]),
    ("the same meeting twice", [[[600, 660], [600, 660]], [[600, 660]]], [[540, 600], [660, 1020]]),
    ("meetings listed latest first", [[[900, 960], [700, 760], [600, 630]]], [[540, 600], [630, 700], [760, 900], [960, 1020]]),
    ("a chain of overlaps", [[[600, 700], [740, 800]], [[650, 750]]], [[540, 600], [800, 1020]]),
    ("overlaps across three people", [[[600, 640]], [[620, 700]], [[690, 710], [900, 1000]]], [[540, 600], [710, 900], [1000, 1020]]),
    ("a short meeting after a long one it sits inside", [[[560, 1000], [990, 995]]], [[540, 560], [1000, 1020]]),
]
for label, busy, expected in FIXED:
    request = {"workday": DAY, "min_length": 1, "busy": busy}
    compare(problems, label, request, expected)
    cases += 1

# With a quorum below the whole group, a person counts once however many of their own intervals
# cover a minute, while the same meeting in two people's lists makes two busy people.
QUORUM = [
    ("one person's overlapping meetings, quorum 2 of 3", [[[600, 700], [650, 750]], [], []], 2, [[540, 1020]]),
    ("one person's repeated meeting, quorum 1 of 2", [[[600, 660], [600, 660], [600, 660]], []], 1, [[540, 1020]]),
    ("one person's nested meetings, quorum 1 of 2", [[[600, 800], [650, 700]], [[700, 760]]], 1, [[540, 700], [760, 1020]]),
    ("one person's meetings nested three deep, quorum 2 of 3", [[[600, 900], [650, 850], [700, 800]], [[720, 780]], []], 2, [[540, 720], [780, 1020]]),
    ("the same meeting for two people, quorum 2 of 3", [[[600, 660]], [[600, 660]], []], 2, [[540, 600], [660, 1020]]),
    ("the same meeting for two people, quorum 1 of 3", [[[600, 660]], [[600, 660]], []], 1, [[540, 1020]]),
    ("overlaps within and across people, quorum 2 of 4", [[[600, 700], [620, 640], [690, 760]], [[650, 720], [650, 720]], [], [[900, 950]]], 2, [[540, 1020]]),
    ("overlaps within and across people, quorum 3 of 4", [[[600, 700], [620, 640], [690, 760]], [[650, 720], [650, 720]], [], [[900, 950]]], 3, [[540, 650], [720, 1020]]),
]
for label, busy, quorum, expected in QUORUM:
    request = {"workday": DAY, "min_length": 1, "quorum": quorum, "busy": busy}
    compare(problems, label, request, expected)
    cases += 1

# The answer stays the same when intervals are shuffled, repeated or split into overlapping
# pieces, and when the people are listed in another order.
rng = random.Random(5050)
for number in range(45):
    request = random_request(rng, nested=True, people=rng.randint(1, 5))
    expected = expected_slots(request)
    compare(problems, f"generated request {number}", request, expected)
    variant = copy.deepcopy(request)
    for person in variant["busy"]:
        extra = []
        for start, end in person:
            if end - start >= 4 and rng.random() < 0.4:
                cut = rng.randrange(start + 2, end - 1)
                extra.append([start, cut + 1])
                extra.append([cut - 1, end])
            if rng.random() < 0.2:
                extra.append([start, end])
        person.extend(extra)
        rng.shuffle(person)
    rng.shuffle(variant["busy"])
    compare(problems, f"generated request {number}, reshuffled", variant, expected)
    cases += 2

finish(problems, f"overlaps ok: {cases} requests")
