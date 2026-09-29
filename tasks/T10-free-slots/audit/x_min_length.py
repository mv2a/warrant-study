"""X6 (G2): stretches of at least min_length minutes are returned, shorter ones never.

Answers are compared as sets of minutes against the audit's own model, and an answer with
nothing long enough must be an empty list.
"""

import random

from _cmd import call, finish
from _model import all_of, describe, expected, free_stretches, minutes, random_busy, random_quorum, random_workday, slots_of

W = [540, 1020]
TWO = [[[600, 660]], [[800, 860]]]  # free stretches: [540,600] 60, [660,800] 140, [860,1020] 160
THREE = [[[600, 660]], [[630, 700]], [[900, 960]]]  # with quorum 2: [540,630] 90, [660,1020] 360
CASES = [
    # Exactly min_length is enough; one minute more is not.
    {"workday": W, "min_length": 60, "busy": TWO},
    {"workday": W, "min_length": 61, "busy": TWO},
    {"workday": W, "min_length": 140, "busy": TWO},
    {"workday": W, "min_length": 141, "busy": TWO},
    {"workday": W, "min_length": 160, "busy": TWO},
    {"workday": W, "min_length": 161, "busy": TWO},
    {"workday": W, "min_length": 59, "busy": TWO},
    # A stretch between two meetings that lasts exactly min_length.
    {"workday": W, "min_length": 37, "busy": [[[540, 700]], [[737, 1020]]]},
    {"workday": W, "min_length": 38, "busy": [[[540, 700]], [[737, 1020]]]},
    # One free minute: kept for min_length 1, dropped for 2.
    {"workday": W, "min_length": 1, "busy": [[[540, 777], [778, 1020]]]},
    {"workday": W, "min_length": 2, "busy": [[[540, 777], [778, 1020]]]},
    # The whole working day as one stretch, exactly long enough and one minute short.
    {"workday": W, "min_length": 480, "busy": [[]]},
    {"workday": W, "min_length": 481, "busy": [[]]},
    {"workday": [0, 1440], "min_length": 1440, "busy": [[], []]},
    {"workday": [0, 1440], "min_length": 1441, "busy": [[]]},
    # min_length far beyond a day is still a valid request with no slots.
    {"workday": [0, 1440], "min_length": 100000, "busy": [[]]},
    # Nothing long enough: an empty list.
    {"workday": W, "min_length": 200, "busy": TWO},
    {"workday": W, "min_length": 30, "busy": [[[540, 560], [580, 600], [620, 640]], [[629, 1020]]]},
    # Several stretches of equal length at the threshold.
    {"workday": W, "min_length": 20, "busy": [[[560, 600], [620, 660], [680, 720], [740, 1020]]]},
    {"workday": W, "min_length": 21, "busy": [[[560, 600], [620, 660], [680, 720], [740, 1020]]]},
    # Stretches shaped by a quorum of two of three people: only 630-660, when two are busy, is not free.
    {"workday": W, "min_length": 90, "quorum": 2, "busy": THREE},
    {"workday": W, "min_length": 91, "quorum": 2, "busy": THREE},
    {"workday": W, "min_length": 360, "quorum": 2, "busy": THREE},
    {"workday": W, "min_length": 361, "quorum": 2, "busy": THREE},
    # A quorum of one: the only stretch that is not free is when all three are busy, 640-650.
    {"workday": W, "min_length": 100, "quorum": 1, "busy": [[[600, 700]], [[620, 650]], [[640, 660]]]},
    {"workday": W, "min_length": 101, "quorum": 1, "busy": [[[600, 700]], [[620, 650]], [[640, 660]]]},
]
CASES = [all_of(request) for request in CASES]

rng = random.Random(4242_77)
while len(CASES) < 106:
    workday = random_workday(rng)
    busy = random_busy(rng, workday, spill=30, longest=120)
    quorum = random_quorum(rng, busy)
    stretches = free_stretches(workday, busy, quorum)
    if not stretches:
        continue
    pick = rng.choice(stretches)
    length = pick[1] - pick[0]
    for need in (length, length + 1) if rng.random() < 0.7 else (max(1, length - 1), rng.randint(1, 1440)):
        CASES.append({"workday": workday, "min_length": need, "quorum": quorum, "busy": busy})

problems = []
for request in CASES:
    status, body = call(request)
    got = slots_of(status, body)
    if got is None:
        problems.append(f"{describe(request)}: no usable answer (status {status}, {str(body)[:60]})")
        continue
    want = expected(request)
    if not want and got != []:
        problems.append(f"{describe(request)}: nothing lasts {request['min_length']} minutes, expected [], got {got[:4]}")
    elif minutes(got) != minutes(want):
        problems.append(f"{describe(request)}: expected {want[:4]}, got {got[:4]}")

finish(problems, f"min-length ok: {len(CASES)} requests")
