"""H4 (C1): intervals run from start up to, but not including, end; touching meetings leave no gap."""

import random

from _cmd import finish
from _oracle import compare, random_request

problems = []
cases = 0

FIXED = [
    ("a slot starts the minute a meeting ends", {"workday": [540, 780], "min_length": 30, "busy": [[[600, 660]]]}, [[540, 600], [660, 780]]),
    ("touching meetings of one person", {"workday": [540, 780], "min_length": 1, "busy": [[[600, 660], [660, 720]]]}, [[540, 600], [720, 780]]),
    ("touching meetings of two people", {"workday": [540, 780], "min_length": 1, "busy": [[[600, 660]], [[660, 720]]]}, [[540, 600], [720, 780]]),
    ("a chain of touching meetings", {"workday": [480, 900], "min_length": 1, "busy": [[[500, 530], [560, 600]], [[530, 560], [600, 640]], [[640, 700]]]}, [[480, 500], [700, 900]]),
    ("a one-minute gap", {"workday": [540, 780], "min_length": 1, "busy": [[[600, 660]], [[661, 720]]]}, [[540, 600], [660, 661], [720, 780]]),
    ("a one-minute gap is too short for two", {"workday": [540, 780], "min_length": 2, "busy": [[[600, 660]], [[661, 720]]]}, [[540, 600], [720, 780]]),
    ("a gap of exactly 30 minutes between meetings", {"workday": [540, 780], "min_length": 30, "busy": [[[560, 660]], [[690, 780]]]}, [[660, 690]]),
    ("a gap of 30 minutes is too short for 31", {"workday": [540, 780], "min_length": 31, "busy": [[[560, 660]], [[690, 780]]]}, []),
    ("a one-minute meeting", {"workday": [540, 780], "min_length": 1, "busy": [[[600, 601]]]}, [[540, 600], [601, 780]]),
    ("midnight to midnight", {"workday": [0, 1440], "min_length": 1, "busy": [[[0, 1], [1439, 1440]]]}, [[1, 1439]]),
    ("a meeting all day", {"workday": [0, 1440], "min_length": 1, "busy": [[[0, 1440]]]}, []),
    ("a meeting ending as the working hours start", {"workday": [540, 600], "min_length": 60, "busy": [[[480, 540]]]}, [[540, 600]]),
    ("a meeting starting as the working hours end", {"workday": [540, 600], "min_length": 60, "busy": [[[600, 660]]]}, [[540, 600]]),
    ("touching meetings of two people, quorum 1 of 2", {"workday": [540, 780], "min_length": 1, "quorum": 1, "busy": [[[600, 660]], [[660, 720]]]}, [[540, 780]]),
    ("a person is free again at the minute their meeting ends", {"workday": [540, 780], "min_length": 1, "quorum": 2, "busy": [[[600, 660]], [[659, 700]], [[640, 700]]]}, [[540, 640], [700, 780]]),
    ("a one-minute overlap, quorum 1 of 2", {"workday": [540, 780], "min_length": 1, "quorum": 1, "busy": [[[600, 661]], [[660, 720]]]}, [[540, 660], [661, 780]]),
    ("touching meetings in a ring of three, quorum 2 of 3", {"workday": [540, 780], "min_length": 1, "quorum": 2, "busy": [[[600, 640], [680, 720]], [[640, 680]], [[720, 760]]]}, [[540, 780]]),
]
for label, request, expected in FIXED:
    compare(problems, label, request, expected)
    cases += 1

# Generated requests where most meetings start exactly when the previous one ends.
rng = random.Random(4040)
for number in range(60):
    request = random_request(rng, touching=0.8, min_length=rng.choice([1, 1, 2, 5, 15, 30]))
    compare(problems, f"generated request {number}", request)
    cases += 1

finish(problems, f"touching ok: {cases} requests")
