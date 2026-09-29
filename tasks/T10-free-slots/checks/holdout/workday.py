"""H6 (C3): slots lie within the working hours; meetings are cut at their edges, not dropped."""

import random

from _cmd import finish
from _oracle import compare, expected_slots, random_request, slots_of

problems = []
cases = 0

DAY = [540, 1020]
FIXED = [
    ("a meeting running past the start", [[[480, 600]]], [[600, 1020]]),
    ("a meeting running past the end", [[[960, 1080]]], [[540, 960]]),
    ("a meeting covering the whole working day", [[[500, 1100]]], []),
    ("meetings past both edges", [[[0, 570]], [[990, 1440]]], [[570, 990]]),
    ("meetings entirely outside", [[[0, 100], [300, 540]], [[1020, 1100], [1300, 1440]]], [[540, 1020]]),
    ("free time reaching both edges", [[[700, 800]]], [[540, 700], [800, 1020]]),
    ("a meeting past the start and one inside", [[[520, 560]], [[580, 600]]], [[560, 580], [600, 1020]]),
    ("a meeting past the end and one inside", [[[900, 930]], [[1000, 1200]]], [[540, 900], [930, 1000]]),
    ("a meeting past the start nested in a longer one", [[[400, 700], [500, 560]]], [[700, 1020]]),
]
for label, busy, expected in FIXED:
    compare(problems, label, {"workday": DAY, "min_length": 1, "busy": busy}, expected)
    cases += 1

# Working hours other than nine to five.
compare(problems, "working hours all day", {"workday": [0, 1440], "min_length": 60, "busy": [[[600, 700]]]}, [[0, 600], [700, 1440]])
compare(problems, "late shift", {"workday": [1200, 1440], "min_length": 30, "busy": [[[1100, 1230]], [[1400, 1440]]]}, [[1230, 1400]])
compare(problems, "early shift", {"workday": [0, 300], "min_length": 30, "busy": [[[250, 400]], [[0, 20]]]}, [[20, 250]])
compare(problems, "short working hours", {"workday": [600, 630], "min_length": 10, "busy": [[[560, 605], [625, 700]]]}, [[605, 625]])
cases += 4

# Clipped meetings still make their person busy when a quorum is counted.
compare(problems, "two meetings past the start, quorum 1 of 2", {"workday": DAY, "min_length": 1, "quorum": 1, "busy": [[[480, 600]], [[500, 560]]]}, [[560, 1020]])
compare(problems, "two meetings past the end, quorum 2 of 3", {"workday": DAY, "min_length": 1, "quorum": 2, "busy": [[[950, 1100]], [[990, 1440]], []]}, [[540, 990]])
compare(problems, "a meeting outside and one past the start, quorum 1 of 2", {"workday": DAY, "min_length": 1, "quorum": 1, "busy": [[[0, 540]], [[400, 600]]]}, [[540, 1020]])
cases += 3

# Generated requests with meetings on both sides of the working hours: every slot lies inside them.
rng = random.Random(6060)
for number in range(60):
    request = random_request(rng)
    day_start, day_end = request["workday"]
    for person in request["busy"]:
        if rng.random() < 0.5 and day_start > 0:
            person.append([rng.randrange(0, day_start), rng.randrange(day_start, day_end) + 1])
        if rng.random() < 0.5 and day_end < 1440:
            person.append([rng.randrange(day_start, day_end), rng.randrange(day_end, 1440) + 1])
    status, slots = slots_of(request)
    cases += 1
    if status == 0 and isinstance(slots, list):
        outside = [s for s in slots if not (isinstance(s, list) and len(s) == 2 and day_start <= s[0] and s[1] <= day_end)]
        if outside:
            problems.append(f"generated request {number}: slots outside {request['workday']}: {outside}")
            continue
    compare(problems, f"generated request {number}", request)

finish(problems, f"working hours ok: {cases} requests")
