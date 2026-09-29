"""X10 (C3): slots lie within the working hours, which clip meetings and free time alike.

Slots are compared, sorted, with answers worked out by hand below and, for generated
requests whose meetings straddle the edges of the working hours, with the audit's model.
"""

import random

from _cmd import call, finish
from _model import all_of, describe, expected, random_interval, random_quorum, random_workday, slots_of

W = [540, 1020]
CASES = [
    # Meetings that run past the start or the end still block the part inside.
    ({"workday": W, "min_length": 1, "busy": [[[480, 600]]]}, [[600, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[1000, 1100]]]}, [[540, 1000]]),
    ({"workday": W, "min_length": 1, "busy": [[[0, 541]], [[1019, 1440]]]}, [[541, 1019]]),
    ({"workday": W, "min_length": 1, "busy": [[[300, 1300]]]}, []),
    ({"workday": W, "min_length": 1, "busy": [[[0, 1440]]]}, []),
    ({"workday": W, "min_length": 1, "busy": [[[540, 1020]]]}, []),
    # Meetings entirely outside, or only touching the edges, change nothing.
    ({"workday": W, "min_length": 1, "busy": [[[0, 540]]]}, [[540, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[1020, 1440]]]}, [[540, 1020]]),
    ({"workday": W, "min_length": 480, "busy": [[[0, 540], [1020, 1440]], [[100, 200]], [[1200, 1300]]]}, [[540, 1020]]),
    ({"workday": W, "min_length": 1, "busy": [[[30, 60], [1400, 1440]], [[539, 540]]]}, [[540, 1020]]),
    # Free time that reaches the edges ends there, however free the minutes outside are.
    ({"workday": W, "min_length": 60, "busy": [[[600, 960]]]}, [[540, 600], [960, 1020]]),
    ({"workday": W, "min_length": 61, "busy": [[[600, 960]]]}, []),
    ({"workday": [600, 660], "min_length": 61, "busy": [[]]}, []),
    ({"workday": [600, 660], "min_length": 60, "busy": [[]]}, [[600, 660]]),
    # A clipped meeting leaves exactly the time inside the working hours.
    ({"workday": W, "min_length": 440, "busy": [[[500, 580]]]}, [[580, 1020]]),
    ({"workday": W, "min_length": 441, "busy": [[[500, 580]]]}, []),
    ({"workday": W, "min_length": 450, "busy": [[[990, 1100]]]}, [[540, 990]]),
    ({"workday": W, "min_length": 451, "busy": [[[990, 1100]]]}, []),
    # Tiny working hours.
    ({"workday": [700, 701], "min_length": 1, "busy": [[[650, 700]], [[701, 760]]]}, [[700, 701]]),
    ({"workday": [700, 701], "min_length": 1, "busy": [[[650, 701]]]}, []),
    ({"workday": [700, 701], "min_length": 1, "busy": [[[700, 760]]]}, []),
    # Working hours at the ends of the day.
    ({"workday": [0, 120], "min_length": 1, "busy": [[[60, 600]]]}, [[0, 60]]),
    ({"workday": [1320, 1440], "min_length": 1, "busy": [[[0, 1380]]]}, [[1380, 1440]]),
    # Under a quorum, the part of a meeting inside the working hours still makes its person busy.
    ({"workday": W, "min_length": 1, "quorum": 1, "busy": [[[400, 620]], [[510, 580]]]}, [[580, 1020]]),
    ({"workday": W, "min_length": 1, "quorum": 2, "busy": [[[1000, 1200]], [[970, 1300]], [[1010, 1440]]]}, [[540, 1000]]),
    ({"workday": W, "min_length": 1, "quorum": 1, "busy": [[[0, 540], [700, 720]], [[1020, 1440], [710, 730]]]}, [[540, 710], [720, 1020]]),
    ({"workday": W, "min_length": 1, "quorum": 2, "busy": [[[0, 1440]], [[300, 560]], [[1000, 1100]]]}, [[560, 1000]]),
]
CASES = [(all_of(request), want) for request, want in CASES]

rng = random.Random(27_1828)
for _ in range(60):
    workday = random_workday(rng)
    ws, we = workday
    busy = []
    for _ in range(rng.randint(1, 4)):
        person = []
        for _ in range(rng.randint(0, 4)):
            kind = rng.random()
            if kind < 0.3 and ws > 0:      # straddles the start
                s = rng.randrange(max(0, ws - 200), ws)
                person.append([s, rng.randint(ws + 1, min(1440, we + 50))])
            elif kind < 0.6 and we < 1440:  # straddles the end
                e = rng.randint(we + 1, min(1440, we + 200))
                person.append([rng.randrange(max(0, ws - 50), we), e])
            elif kind < 0.8:              # entirely outside, or touching an edge
                if ws > 0 and (we == 1440 or rng.random() < 0.5):
                    person.append(random_interval(rng, 0, ws, 300) if rng.random() < 0.6 else [rng.randrange(0, ws), ws])
                elif we < 1440:
                    person.append(random_interval(rng, we, 1440, 300) if rng.random() < 0.6 else [we, rng.randint(we + 1, 1440)])
            else:                         # inside
                person.append(random_interval(rng, ws, we, 60))
        busy.append(person)
    CASES.append(({"workday": workday, "min_length": rng.choice([1, 1, 10, rng.randint(1, we - ws + 1)]), "quorum": random_quorum(rng, busy), "busy": busy}, None))

problems = []
for request, want in CASES:
    if want is None:
        want = expected(request)
    status, body = call(request)
    got = slots_of(status, body)
    if got is None:
        problems.append(f"{describe(request)}: no usable answer (status {status}, {str(body)[:60]})")
        continue
    ws, we = request["workday"]
    outside = [s for s in got if s[0] < ws or s[1] > we]
    if outside:
        problems.append(f"{describe(request)}: slots {outside[:3]} lie outside the working hours {request['workday']}")
    elif sorted(got) != want:
        problems.append(f"{describe(request)}: expected {want[:5]}, got {got[:5]}")

finish(problems, f"working-hours ok: {len(CASES)} requests")
