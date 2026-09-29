"""X8 (C1): intervals are [start, end) in whole minutes from 0 to 1440; [s, e] lasts e - s.

Slots are compared, sorted, with the answers worked out by hand below and, for the
generated requests on 5- and 15-minute grids, with the audit's own model.
"""

import random

from _cmd import call, finish
from _model import all_of, describe, expected, random_busy, random_quorum, random_workday, slots_of

CASES = [
    # Touching meetings leave no free time between them, for one person or two.
    ({"workday": [540, 1020], "min_length": 1, "busy": [[[600, 660], [660, 720]]]}, [[540, 600], [720, 1020]]),
    ({"workday": [540, 1020], "min_length": 1, "busy": [[[600, 660]], [[660, 720]]]}, [[540, 600], [720, 1020]]),
    ({"workday": [540, 1020], "min_length": 1, "busy": [[[660, 720]], [[600, 660]], [[720, 780]]]}, [[540, 600], [780, 1020]]),
    # A slot starts at the minute a meeting ends and ends at the minute the next one starts.
    ({"workday": [540, 1020], "min_length": 1, "busy": [[[540, 610], [655, 1020]]]}, [[610, 655]]),
    ({"workday": [540, 1020], "min_length": 1, "busy": [[[540, 610]], [[655, 1020]]]}, [[610, 655]]),
    # A one-minute gap is free, and a one-minute meeting blocks one minute.
    ({"workday": [540, 1020], "min_length": 1, "busy": [[[540, 700], [701, 1020]]]}, [[700, 701]]),
    ({"workday": [700, 703], "min_length": 1, "busy": [[[701, 702]]]}, [[700, 701], [702, 703]]),
    # [s, e] lasts e - s minutes: two 40-minute stretches pass min_length 40 and fail 41.
    ({"workday": [560, 680], "min_length": 40, "busy": [[[600, 640]]]}, [[560, 600], [640, 680]]),
    ({"workday": [560, 680], "min_length": 41, "busy": [[[600, 640]]]}, []),
    ({"workday": [560, 680], "min_length": 39, "busy": [[[600, 640]]]}, [[560, 600], [640, 680]]),
    # A 1-minute workday lasts one minute.
    ({"workday": [1439, 1440], "min_length": 1, "busy": [[]]}, [[1439, 1440]]),
    ({"workday": [0, 1], "min_length": 1, "busy": [[]]}, [[0, 1]]),
    ({"workday": [0, 1], "min_length": 2, "busy": [[]]}, []),
    # Minutes 0 and 1440 are the ends of the day.
    ({"workday": [0, 1440], "min_length": 1, "busy": [[[0, 1], [1439, 1440]]]}, [[1, 1439]]),
    ({"workday": [0, 1440], "min_length": 1438, "busy": [[[0, 1]], [[1439, 1440]]]}, [[1, 1439]]),
    ({"workday": [0, 1440], "min_length": 1, "busy": [[[0, 720]], [[720, 1440]]]}, []),
    ({"workday": [0, 1440], "min_length": 1, "busy": [[[0, 719]], [[720, 1440]]]}, [[719, 720]]),
    ({"workday": [0, 1440], "min_length": 1, "busy": [[[1, 1440]]]}, [[0, 1]]),
    # A person is free again at the minute their meeting ends, also when a quorum is counted.
    ({"workday": [480, 900], "min_length": 1, "quorum": 1, "busy": [[[620, 680]], [[680, 750]]]}, [[480, 900]]),
    ({"workday": [540, 1020], "min_length": 1, "quorum": 2, "busy": [[[600, 700]], [[700, 760]], [[650, 700]]]}, [[540, 650], [700, 1020]]),
    ({"workday": [540, 1020], "min_length": 1, "quorum": 1, "busy": [[[600, 701]], [[700, 760]]]}, [[540, 700], [701, 1020]]),
    ({"workday": [540, 1020], "min_length": 1, "quorum": 2, "busy": [[[600, 640], [640, 680]], [[680, 720]], [[640, 641]]]}, [[540, 640], [641, 1020]]),
    ({"workday": [0, 1440], "min_length": 1, "quorum": 1, "busy": [[[0, 720]], [[720, 1440]]]}, [[0, 1440]]),
]
CASES = [(all_of(request), want) for request, want in CASES]

rng = random.Random(5_31_2026)
for _ in range(50):
    workday = random_workday(rng)
    grid = rng.choice([5, 15])
    workday = [workday[0] - workday[0] % grid, workday[1]]
    if workday[1] - workday[1] % grid > workday[0]:
        workday[1] -= workday[1] % grid
    busy = random_busy(rng, workday, grid=grid, spill=30, longest=60)
    CASES.append(({"workday": workday, "min_length": rng.choice([1, grid, grid + 1, 2 * grid]), "quorum": random_quorum(rng, busy), "busy": busy}, None))

problems = []
for request, want in CASES:
    if want is None:
        want = expected(request)
    status, body = call(request)
    got = slots_of(status, body)
    if got is None:
        problems.append(f"{describe(request)}: no usable answer (status {status}, {str(body)[:60]})")
    elif sorted(got) != want:
        problems.append(f"{describe(request)}: expected {want[:5]}, got {got[:5]}")

finish(problems, f"minutes ok: {len(CASES)} requests")
