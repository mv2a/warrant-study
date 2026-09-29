"""X5 (G1): a minute is in a slot only when at least quorum of the listed people are free at it.

Answers are compared as sets of minutes against the audit's own model, so this check
looks at which minutes are offered, not at how they are grouped into slots (that is G3).
"""

import random

from _cmd import call, finish
from _model import all_of, describe, expected, minutes, random_busy, random_quorum, random_workday, slots_of

W = [480, 1080]
CASES = [
    # Everyone required: one busy person blocks the group, wherever they sit in the list.
    {"workday": W, "min_length": 1, "busy": [[[600, 690]], [], [], [], []]},
    {"workday": W, "min_length": 1, "busy": [[], [], [[600, 690]], [], []]},
    {"workday": W, "min_length": 1, "busy": [[], [], [], [], [[600, 690]]]},
    # Everyone required, people busy at different times: only minutes free for all of them count.
    {"workday": W, "min_length": 1, "busy": [[[500, 530]], [[620, 700]], [[850, 1000]]]},
    {"workday": W, "min_length": 1, "busy": [[[480, 780]], [[780, 1080]]]},
    {"workday": W, "min_length": 1, "busy": [[[480, 700]], [[650, 1080]]]},
    # Four of five required: one busy person, wherever listed, blocks nothing; two at once do.
    {"workday": W, "min_length": 1, "quorum": 4, "busy": [[[600, 690]], [], [], [], []]},
    {"workday": W, "min_length": 1, "quorum": 4, "busy": [[], [], [], [], [[600, 690]]]},
    {"workday": W, "min_length": 1, "quorum": 4, "busy": [[], [[620, 680]], [], [[650, 700]], []]},
    {"workday": W, "min_length": 1, "quorum": 4, "busy": [[[500, 1000]], [[520, 540], [990, 1010]], [], [], []]},
    # One person required: time is free unless everyone is busy.
    {"workday": W, "min_length": 1, "quorum": 1, "busy": [[[480, 780]], [[700, 1080]]]},
    {"workday": W, "min_length": 1, "quorum": 1, "busy": [[[500, 600], [800, 900]], [[550, 850]], [[590, 810]]]},
    # A meeting held by three of four people, for each quorum.
    {"workday": W, "min_length": 1, "quorum": 1, "busy": [[[700, 760]], [[700, 760]], [], [[700, 760]]]},
    {"workday": W, "min_length": 1, "quorum": 2, "busy": [[[700, 760]], [[700, 760]], [], [[700, 760]]]},
    {"workday": W, "min_length": 1, "quorum": 3, "busy": [[[700, 760]], [[700, 760]], [], [[700, 760]]]},
    # A person with no busy intervals is free all day and counts toward the quorum.
    {"workday": W, "min_length": 1, "busy": [[]]},
    {"workday": W, "min_length": 1, "busy": [[], [], [], [], [], [], []]},
    {"workday": [0, 1440], "min_length": 1, "busy": [[]]},
    {"workday": W, "min_length": 10, "busy": [[], [[700, 720]], []]},
    {"workday": W, "min_length": 1, "quorum": 1, "busy": [[], [[480, 1080]]]},
    {"workday": W, "min_length": 1, "quorum": 2, "busy": [[], [[480, 1080]]]},
    {"workday": W, "min_length": 1, "quorum": 2, "busy": [[[480, 1080]], [], [[600, 660]]]},
    {"workday": W, "min_length": 1, "quorum": 3, "busy": [[], [[540, 700]], [], [[650, 900]], []]},
    # The first person free but the others not, and the other way round.
    {"workday": W, "min_length": 1, "busy": [[], [[480, 1080]]]},
    {"workday": W, "min_length": 1, "busy": [[[480, 1080]], []]},
    {"workday": W, "min_length": 1, "busy": [[[481, 1079]], [[480, 481]], [[1079, 1080]]]},
    # Many people: 200 people, each busy for a different single minute, all or all but one required.
    {"workday": W, "min_length": 1, "busy": [[[480 + 3 * k, 481 + 3 * k]] for k in range(200)]},
    {"workday": W, "min_length": 1, "quorum": 199, "busy": [[[480 + 3 * k, 481 + 3 * k]] for k in range(200)]},
    # 600 people with nothing booked and one person, last, who is busy.
    {"workday": W, "min_length": 1, "busy": [[] for _ in range(600)] + [[[700, 760]]]},
    {"workday": W, "min_length": 1, "quorum": 600, "busy": [[] for _ in range(600)] + [[[700, 760]]]},
    # 60 people whose meetings leave one shared gap between 900 and 905, and a quorum of 50 of them.
    {"workday": W, "min_length": 1, "busy": [[[480, 900], [905 + k, 1080]] for k in range(60)]},
    {"workday": W, "min_length": 1, "quorum": 50, "busy": [[[480, 900], [905 + k, 1080]] for k in range(60)]},
    # Ten people each busy for 100 minutes, starting 40 minutes apart, with eight required.
    {"workday": W, "min_length": 1, "quorum": 8, "busy": [[[500 + 40 * k, 600 + 40 * k]] for k in range(10)]},
]
CASES = [all_of(request) for request in CASES]

rng = random.Random(1010_2026)
for _ in range(70):
    workday = random_workday(rng)
    people = rng.choice([1, 2, 3, 5, 8, 13, 25, 40])
    busy = random_busy(rng, workday, people=people, per_person=None, spill=60, longest=90)
    if rng.random() < 0.3:
        busy.insert(rng.randrange(len(busy) + 1), [])
    CASES.append({"workday": workday, "min_length": 1, "quorum": random_quorum(rng, busy), "busy": busy})

problems = []
for request in CASES:
    status, body = call(request)
    got = slots_of(status, body)
    if got is None:
        problems.append(f"{describe(request)}: no usable answer (status {status}, {str(body)[:60]})")
        continue
    want = minutes(expected(request))
    have = minutes(got)
    if have != want:
        extra = sorted(have - want)[:3]
        missing = sorted(want - have)[:3]
        problems.append(f"{describe(request)}: minutes wrongly offered {extra}, free minutes left out {missing}")

finish(problems, f"enough-free ok: {len(CASES)} requests")
