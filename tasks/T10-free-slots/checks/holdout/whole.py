"""H3 (G3): each free stretch comes back whole, in time order, with no two slots overlapping or touching."""

import random

from _cmd import finish
from _oracle import compare, expected_slots, random_request, slots_of

problems = []
cases = 0

FIXED = [
    ("a long free stretch is not cut into pieces", {"workday": [0, 1440], "min_length": 15, "busy": [[[300, 310]]]}, [[0, 300], [310, 1440]]),
    ("stretches from longest to shortest", {"workday": [540, 1020], "min_length": 20, "busy": [[[740, 760]], [[900, 920]]]}, [[540, 740], [760, 900], [920, 1020]]),
    ("stretches from shortest to longest", {"workday": [540, 1020], "min_length": 20, "busy": [[[570, 600], [650, 700]], [[780, 800]]]}, [[540, 570], [600, 650], [700, 780], [800, 1020]]),
    ("stretches of equal length", {"workday": [480, 780], "min_length": 30, "busy": [[[540, 600]], [[660, 720]]]}, [[480, 540], [600, 660], [720, 780]]),
    ("a stretch where the free person changes", {"workday": [480, 960], "min_length": 30, "busy": [[[480, 600], [800, 960]], [[480, 540], [700, 960]]]}, [[600, 700]]),
    ("one long stretch and many short ones", {"workday": [540, 1020], "min_length": 10, "busy": [[[550, 556], [565, 570], [580, 592]], [[600, 610]]]}, [[540, 550], [570, 580], [610, 1020]]),
    ("people busy in turn, quorum 2 of 3", {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 660]], [[660, 720]], [[720, 780]]]}, [[540, 1020]]),
    ("people busy in turn, quorum 3 of 3", {"workday": [540, 1020], "min_length": 30, "quorum": 3, "busy": [[[600, 660]], [[660, 720]], [[720, 780]]]}, [[540, 600], [780, 1020]]),
    ("a handover with an overlap, quorum 2 of 3", {"workday": [540, 1020], "min_length": 30, "quorum": 2, "busy": [[[600, 700]], [[650, 760]], [[900, 960]]]}, [[540, 650], [700, 1020]]),
    ("short busy spells inside a long stretch, quorum 3 of 4", {"workday": [480, 960], "min_length": 120, "quorum": 3, "busy": [[[500, 510], [700, 705]], [[520, 530]], [], [[800, 900]]]}, [[480, 960]]),
    ("a quorum stretch longest first", {"workday": [480, 960], "min_length": 20, "quorum": 1, "busy": [[[700, 760], [900, 930]], [[700, 760], [850, 880], [900, 915], [930, 960]]]}, [[480, 700], [760, 900], [915, 960]]),
]
for label, request, expected in FIXED:
    compare(problems, label, request, expected)
    cases += 1

# Generated requests: slots are strictly increasing, separated by busy time, and each is a
# whole free stretch (the minute before it and the minute at its end are not free working time).
rng = random.Random(3030)
for number in range(80):
    request = random_request(rng)
    expected = expected_slots(request)
    status, slots = slots_of(request)
    cases += 1
    if status != 0 or not isinstance(slots, list):
        problems.append(f"generated request {number}: no answer (status {status})")
        continue
    ordered = all(isinstance(s, list) and len(s) == 2 for s in slots) and all(
        a[1] < b[0] for a, b in zip(slots, slots[1:])
    )
    if not ordered:
        problems.append(f"generated request {number}: slots overlap, touch or are out of order: {slots}")
    elif slots != expected:
        problems.append(f"generated request {number}: expected {expected}, got {slots}")

finish(problems, f"whole stretches ok: {cases} requests")
