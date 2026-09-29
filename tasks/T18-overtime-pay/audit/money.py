"""X: pricing in whole cents (C1).

For every response, each category's cents must be rate x multiplier x the category's
minutes / 60, worked out once from the week's totals in the response and rounded to the
nearest cent with exact halves up, and total_cents must be the sum of the three rounded
amounts. Cases cover exact halves on both sides of an even and odd cent in every category,
amounts just below and above a half, minutes from several days (and from the weekly cap
and day 7) priced together rather than day by day, the largest rates and weeks, amounts
that floating-point arithmetic tends to round wrongly, and fixed-seed generated weeks.
"""

import random

from _cmd import call, finish
from _expect import CENT_FIELDS, call_all, minutes_of, prices

CASES = [
    # regular time: exact halves, and just below or above a half
    ([30, 0, 0, 0, 0, 0, 0], 1),         # 0.5
    ([90, 0, 0, 0, 0, 0, 0], 1),         # 1.5
    ([150, 0, 0, 0, 0, 0, 0], 1),        # 2.5
    ([0, 0, 10, 0, 0, 0, 0], 3),         # 0.5
    ([0, 30, 0, 0, 0, 0, 0], 1001),      # 500.5
    ([0, 0, 0, 0, 0, 0, 90], 3333),      # 4999.5
    ([29, 0, 0, 0, 0, 0, 0], 1),         # 0.483
    ([31, 0, 0, 0, 0, 0, 0], 1),         # 0.517
    ([0, 4, 0, 0, 0, 0, 0], 7),          # 0.467
    ([0, 5, 0, 0, 0, 0, 0], 7),          # 0.583
    ([0, 0, 0, 1, 0, 0, 0], 1),          # 0.017
    ([0, 0, 0, 0, 59, 0, 0], 1),         # 0.983
    # overtime: exact halves, and just below or above a half
    ([500, 0, 0, 0, 0, 0, 0], 1),        # 20 min: 0.5
    ([0, 580, 0, 0, 0, 0, 0], 1),        # 100 min: 2.5
    ([0, 0, 484, 0, 0, 0, 0], 5),        # 4 min: 0.5
    ([540, 0, 0, 0, 0, 0, 0], 1),        # 60 min: 1.5
    ([0, 0, 0, 519, 0, 0, 0], 1),        # 39 min: 0.975
    ([0, 0, 0, 0, 493, 0, 0], 1),        # 13 min: 0.325
    ([0, 0, 0, 0, 0, 507, 0], 1),        # 27 min: 0.675
    ([0, 0, 0, 0, 0, 0, 481], 20),       # 1 min: 0.5
    ([0, 0, 0, 0, 0, 0, 482], 7),        # 2 min: 0.35
    # double time: exact halves, and just below or above a half
    ([675, 0, 0, 0, 0, 0, 0], 1),        # 15 min: 0.5
    ([0, 735, 0, 0, 0, 0, 0], 1),        # 75 min: 2.5
    ([0, 0, 665, 0, 0, 0, 0], 3),        # 5 min: 0.5
    ([0, 0, 0, 0, 0, 705, 0], 1),        # 45 min: 1.5
    ([0, 0, 0, 674, 0, 0, 0], 1),        # 14 min: 0.467
    ([0, 0, 0, 0, 676, 0, 0], 1),        # 16 min: 0.533
    ([0, 0, 0, 0, 0, 661, 0], 15),       # 1 min: 0.5
    ([0, 0, 0, 0, 0, 661, 0], 14),       # 1 min: 0.467
    # each category priced once from the week's total, not day by day
    ([500, 500, 0, 0, 0, 0, 0], 1001),
    ([30, 30, 0, 0, 0, 0, 0], 1),
    ([30, 0, 30, 0, 30, 0, 0], 1),
    ([675, 675, 0, 0, 0, 0, 0], 1),
    ([665, 665, 665, 0, 0, 0, 0], 3),
    ([500, 1, 1, 1, 1, 1, 20], 1),
    ([480, 480, 480, 480, 480, 20, 0], 1001),
    ([500, 480, 480, 480, 480, 20, 0], 1001),
    ([1, 1, 1, 1, 1, 1, 481], 1),
    # total_cents is the sum of the three rounded amounts
    ([510, 30, 0, 0, 0, 0, 0], 1),
    ([500, 30, 0, 0, 0, 0, 0], 1),
    ([484, 24, 0, 0, 0, 0, 0], 1),
    ([486, 24, 0, 0, 0, 0, 0], 1),
    ([30, 30, 30, 30, 30, 30, 30], 1),
    # the largest amounts, and the smallest rate
    ([1440, 1440, 1440, 1440, 1440, 1440, 1440], 100000),
    ([1439, 1439, 1439, 1439, 1439, 1439, 1439], 99999),
    ([1440, 1440, 1440, 1440, 1440, 1440, 0], 100000),
    ([1440, 1440, 1440, 1440, 1440, 1440, 1440], 1),
    ([0, 0, 0, 0, 0, 0, 0], 100000),
    # amounts that floating-point formulas tend to round wrongly
    ([0, 0, 0, 0, 1389, 0, 0], 40751),
    ([0, 540, 649, 661, 747, 1127, 0], 55271),
    ([0, 0, 0, 916, 0, 0, 0], 51449),
    ([0, 242, 1383, 0, 0, 0, 0], 95233),
    ([0, 0, 0, 1025, 0, 752, 249], 21130),
    ([0, 477, 821, 0, 327, 0, 0], 48555),
    ([606, 0, 0, 714, 288, 0, 79], 1790),
    ([1161, 1327, 362, 0, 0, 636, 855], 39555),
    ([0, 697, 0, 0, 0, 406, 0], 9265),
    ([1185, 501, 0, 0, 0, 0, 0], 29991),
]

rng = random.Random(95_000_1_5)
for index in range(200):
    week = [rng.choice([0, rng.randint(1, 1440), rng.randint(400, 800)]) for _ in range(7)]
    if index % 5 == 0:
        week = [rng.randint(1, 1440) for _ in range(7)]
    kind = index % 4
    if kind == 0:
        rate = rng.randint(1, 120)
    elif kind == 1:
        rate = rng.randint(121, 5000)
    else:
        rate = rng.randint(5001, 100000)
    CASES.append((week, rate))

problems = []
answers = call_all(call, [{"minutes": week, "rate_cents": rate} for week, rate in CASES])
for (week, rate), (status, body) in zip(CASES, answers):
    minutes = minutes_of(body)
    if status != 0 or minutes is None:
        problems.append(f"{week} at {rate}: expected a paid response, got {body!r} (status {status})")
        continue
    want = dict(zip(CENT_FIELDS + ("total_cents",), prices(rate, *minutes)))
    got = {field: body.get(field) for field in want}
    if got != want or not all(type(value) is int for value in got.values()):
        problems.append(f"{week} at {rate}: for minutes {minutes} expected {want}, got {got}")

finish(problems, f"money ok: {len(CASES)} weeks priced")
