"""H1 (G1): a minute is free when at least quorum people are free at it, however many people there are."""

import random

from _cmd import finish
from _oracle import compare, random_request

problems = []
cases = 0

# With everyone required, one long meeting held by a single person blocks the group, wherever that person is listed.
for size in (2, 3, 4, 5, 7, 10):
    for holder in range(size):
        busy = [[[540 + 20 * k, 550 + 20 * k]] for k in range(size)]
        busy[holder].append([700, 900])
        request = {"workday": [480, 1080], "min_length": 1, "quorum": size, "busy": busy}
        compare(problems, f"{size} people, person {holder + 1} busy 700-900", request)
        cases += 1

# Each of up to twelve people is busy for half of a different hour; with everyone required only the gaps stay free.
for size in range(1, 13):
    busy = [[[480 + 60 * k, 510 + 60 * k]] for k in range(size)]
    request = {"workday": [480, 1260], "min_length": 10, "quorum": size, "busy": busy}
    compare(problems, f"{size} people with one meeting each", request)
    cases += 1

# The same meeting held by some of the group: the time stays free exactly when enough others are free.
for size in (3, 5, 8):
    for held in range(1, size + 1):
        for quorum in range(1, size + 1):
            busy = [[[700, 900]] if k < held else [[1000, 1010]] for k in range(size)]
            request = {"workday": [540, 1020], "min_length": 1, "quorum": quorum, "busy": busy}
            compare(problems, f"{held} of {size} busy 700-900, quorum {quorum}", request)
            cases += 1

# People with no busy intervals are free all day and count toward the quorum.
for size in (1, 2, 5):
    request = {"workday": [540, 1020], "min_length": 30, "quorum": size, "busy": [[] for _ in range(size)]}
    compare(problems, f"{size} people with empty calendars", request, [[540, 1020]])
    request = {"workday": [540, 1020], "min_length": 30, "quorum": 2 * size + 1, "busy": [[]] * size + [[[600, 700]]] + [[]] * size}
    compare(problems, f"one busy person among {2 * size} free ones, everyone required", request, [[540, 600], [700, 1020]])
    request = {"workday": [540, 1020], "min_length": 30, "quorum": size, "busy": [[]] * size + [[[600, 700]]] + [[]] * size}
    compare(problems, f"one busy person among {2 * size} free ones, quorum {size}", request, [[540, 1020]])
    cases += 3
FIXED = [
    ("two busy people and one free all day, quorum 2", [[], [[600, 700]], [[650, 750]]], 2, [[540, 650], [700, 1020]]),
    ("two busy people and one free all day, quorum 1", [[], [[540, 1020]], [[540, 1020]]], 1, [[540, 1020]]),
    ("three free all day and three busy together, quorum 3", [[], [], [], [[600, 700]], [[600, 700]], [[600, 700]]], 3, [[540, 1020]]),
    ("three free all day and three busy together, quorum 4", [[], [], [], [[600, 700]], [[600, 700]], [[600, 700]]], 4, [[540, 600], [700, 1020]]),
    ("a staircase of meetings, quorum 2 of 4", [[[600, 720]], [[630, 750]], [[660, 780]], [[690, 810]]], 2, [[540, 660], [750, 1020]]),
    ("a staircase of meetings, quorum 3 of 4", [[[600, 720]], [[630, 750]], [[660, 780]], [[690, 810]]], 3, [[540, 630], [780, 1020]]),
    ("a staircase of meetings, quorum 1 of 4", [[[600, 720]], [[630, 750]], [[660, 780]], [[690, 810]]], 1, [[540, 690], [720, 1020]]),
]
for label, busy, quorum, expected in FIXED:
    compare(problems, label, {"workday": [540, 1020], "min_length": 1, "quorum": quorum, "busy": busy}, expected)
    cases += 1

# Many generated groups of three to nine people with any quorum, compared with a minute-by-minute count.
rng = random.Random(1010)
for number in range(70):
    request = random_request(rng, people=rng.randint(3, 9), min_length=rng.choice([1, 5, 15, 30]))
    compare(problems, f"generated group {number}", request)
    cases += 1

finish(problems, f"people ok: {cases} requests")
