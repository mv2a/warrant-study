"""H2 (G2): stretches of at least min_length are returned, shorter ones never, and exactly min_length counts."""

import random

from _cmd import finish
from _oracle import compare, layout, random_request

problems = []
cases = 0

# Free stretches one minute short of, exactly at, and one minute over min_length,
# at the start, in the middle and at the end of the working hours.
for need in (1, 2, 15, 30, 45, 60, 90, 120):
    for order in ((-1, 0, 1), (0, 1, -1), (1, -1, 0), (0, 0, 0)):
        pieces = []
        for position, delta in enumerate(order):
            if position:
                pieces.append(("busy", 25))
            if need + delta > 0:
                pieces.append(("free", need + delta))
            elif position:
                pieces.append(("busy", 5))
        workday, busy, free = layout(500, pieces, people=2)
        expected = [stretch for stretch in free if stretch[1] - stretch[0] >= need]
        request = {"workday": workday, "min_length": need, "busy": busy}
        compare(problems, f"min_length {need}, stretches {[b - a for a, b in free]}", request, expected)
        cases += 1

# The whole working hours as one stretch: returned at exactly its length, not one minute more.
for day in ([540, 1020], [0, 1440], [600, 601]):
    length = day[1] - day[0]
    compare(problems, f"free day {day}, min_length {length}", {"workday": day, "min_length": length, "busy": [[]]}, [day])
    compare(problems, f"free day {day}, min_length {length + 1}", {"workday": day, "min_length": length + 1, "busy": [[]]}, [])
    cases += 2

# Stretches shaped by a quorum below the whole group follow the same rule.
TWO = [[[600, 700]], [[640, 760]]]  # with quorum 1 of 2, only 640-700 is not free: stretches of 100 and 320
for need, expected in ((99, [[540, 640], [700, 1020]]), (100, [[540, 640], [700, 1020]]), (101, [[700, 1020]]), (320, [[700, 1020]]), (321, [])):
    compare(problems, f"quorum 1 of 2, min_length {need}", {"workday": [540, 1020], "min_length": need, "quorum": 1, "busy": TWO}, expected)
    cases += 1

# Nothing long enough gives an empty list.
request = {"workday": [540, 1020], "min_length": 100, "busy": [[[600, 700], [790, 880]], [[950, 960]]]}
compare(problems, "no stretch of 100 minutes", request, [])
compare(problems, "min_length 5000", {"workday": [0, 1440], "min_length": 5000, "busy": [[]]}, [])
cases += 2

# Generated requests with a spread of min_length values.
rng = random.Random(2020)
for number in range(60):
    request = random_request(rng, min_length=rng.choice([1, 2, 10, 20, 29, 30, 31, 60, 61, 120, rng.randint(1, 300)]))
    compare(problems, f"generated request {number}", request)
    cases += 1

finish(problems, f"lengths ok: {cases} requests")
