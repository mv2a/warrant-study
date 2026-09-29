"""H4: each category is priced once from its weekly minutes, rounded to the cent with halves up."""

import random

from _cmd import call, finish
from _model import CENT_FIELDS, expected, pick

rng = random.Random(5050)
CASES = [
    ([30, 0, 0, 0, 0, 0, 0], 1001),        # regular 500.5 -> 501
    ([30, 0, 0, 0, 0, 0, 0], 1),           # regular 0.5 -> 1
    ([29, 0, 0, 0, 0, 0, 0], 1),           # regular 0.48 -> 0
    ([1, 0, 0, 0, 0, 0, 0], 30),           # regular 0.5 -> 1
    ([1, 0, 0, 0, 0, 0, 0], 29),           # regular 0.48 -> 0
    ([29, 0, 0, 0, 0, 0, 0], 1001),        # regular 483.82 -> 484
    ([500, 0, 0, 0, 0, 0, 0], 1001),       # overtime 500.5 -> 501
    ([500, 0, 0, 0, 0, 0, 0], 1),          # overtime 0.5 -> 1
    ([487, 0, 0, 0, 0, 0, 0], 3),          # overtime 0.525 -> 1
    ([481, 0, 0, 0, 0, 0, 0], 1),          # overtime 0.025 -> 0
    ([675, 0, 0, 0, 0, 0, 0], 1001),       # double time 500.5 -> 501
    ([675, 0, 0, 0, 0, 0, 0], 1),          # double time 0.5 -> 1
    ([661, 0, 0, 0, 0, 0, 0], 7),          # double time 0.2333 -> 0
    ([490, 490, 0, 0, 0, 0, 0], 1001),     # 20 overtime minutes over two days: 500.5 -> 501, once
    ([500, 500, 0, 0, 0, 0, 0], 1001),     # 40 overtime minutes: exactly 1001
    ([15, 15, 0, 0, 0, 0, 0], 1001),       # 30 regular minutes over two days: 500.5 -> 501, once
    ([15, 15, 15, 15, 0, 0, 0], 1001),     # 60 regular minutes: exactly 1001
    ([670, 670, 670, 0, 0, 0, 0], 1001),   # 30 double-time minutes: exactly 1001
    ([1440, 1440, 1440, 1440, 1440, 1440, 1440], 100000),
    ([1, 1, 1, 1, 1, 1, 1], 1),
    ([0, 0, 0, 0, 0, 0, 0], 99999),
]
for _ in range(70):
    week = [rng.choice([0, rng.randint(1, 1440), rng.randint(1, 60), rng.randint(470, 700)]) for _ in range(7)]
    rate = rng.choice([rng.randint(1, 100000), rng.randrange(1, 100000, 2), rng.randint(1, 40)])
    CASES.append((week, rate))

problems = []
for week, rate in CASES:
    status, body = call({"minutes": week, "rate_cents": rate})
    want = expected(week, rate)
    want_cents, got = pick(want, CENT_FIELDS), pick(body, CENT_FIELDS)
    if status != 0 or got != want_cents:
        problems.append(f"{week} at {rate}: expected regular, overtime, double, total cents {want_cents}, got {got!r}")

finish(problems, f"rounding ok: {len(CASES)} weeks")
