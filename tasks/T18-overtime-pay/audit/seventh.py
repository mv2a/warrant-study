"""X: the seventh consecutive day (G3).

When all seven days have work, day 7's first 480 minutes are overtime and the rest double
time; when any day has 0 minutes, day 7 is an ordinary day. Every week here has fewer than
2400 worked minutes, so the weekly cap cannot matter under any reading. Only the three
minute fields are compared. A fixed-seed generator adds seven-day weeks and weeks with
exactly one day off.
"""

import random

from _cmd import call, finish
from _expect import compare_minutes

weeks = [
    # all seven days worked: day 7 around its 8-hour mark
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 2],
    [1, 1, 1, 1, 1, 1, 479],
    [1, 1, 1, 1, 1, 1, 480],
    [1, 1, 1, 1, 1, 1, 481],
    [1, 1, 1, 1, 1, 1, 660],
    [1, 1, 1, 1, 1, 1, 661],
    [1, 1, 1, 1, 1, 1, 1440],
    [100, 100, 100, 100, 100, 100, 700],
    [240, 240, 240, 240, 240, 240, 660],
    [200, 150, 100, 50, 25, 5, 1200],
    # days 1 to 6 stay ordinary days in a seven-day week
    [700, 1, 1, 1, 1, 1, 500],
    [1, 1, 1, 1, 1, 1440, 30],
    [480, 481, 1, 1, 1, 1, 481],
    [661, 1, 661, 1, 1, 1, 1],
    # a day off anywhere makes day 7 an ordinary day
    [0, 300, 300, 300, 300, 300, 700],
    [300, 0, 300, 300, 300, 300, 700],
    [300, 300, 0, 300, 300, 300, 700],
    [300, 300, 300, 0, 300, 300, 700],
    [300, 300, 300, 300, 0, 300, 700],
    [300, 300, 300, 300, 300, 0, 700],
    [0, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 0, 1, 1, 481],
    [0, 100, 100, 100, 100, 100, 1440],
    [5, 5, 5, 5, 5, 0, 480],
    [0, 0, 0, 0, 0, 0, 661],
    [1, 1, 1, 1, 1, 1, 0],
]

rng = random.Random(7_7_7_1812)
DAY7_POOL = [1, 2, 240, 479, 480, 481, 482, 659, 660, 661, 1000, 1439, 1440]
generated = 0
while generated < 150:
    day_off = generated % 3 == 2
    week = [rng.randint(1, 300) if rng.random() < 0.85 else rng.randint(301, 1440) for _ in range(6)]
    week.append(rng.choice(DAY7_POOL) if rng.random() < 0.5 else rng.randint(1, 1440))
    if day_off:
        week[rng.randrange(6)] = 0
    if sum(week) <= 2399:
        weeks.append(week)
        generated += 1

problems = []
compare_minutes(call, weeks, lambda index: 999 + 113 * index, problems)
finish(problems, f"seventh day ok: {len(weeks)} weeks")
