"""X: the weekly cap in seven-day weeks (G2 with G3).

All seven days have work and days 1 to 6 are at most 8 hours, so their minutes are all
regular before the cap. Day 7's overtime and double time do not count toward the 40
hours, and its double time never becomes overtime. Only the three minute fields are
compared. A fixed-seed generator adds weeks whose regular minutes straddle 2400.
"""

import random

from _cmd import call, finish
from _expect import compare_minutes

weeks = [
    [480, 480, 480, 480, 480, 480, 480],
    [400, 400, 400, 400, 400, 400, 480],
    [400, 400, 400, 400, 400, 400, 1],
    [401, 400, 400, 400, 400, 400, 1],
    [399, 400, 400, 400, 400, 400, 1440],
    [360, 360, 360, 360, 360, 360, 480],
    [360, 360, 360, 360, 360, 360, 1440],
    [480, 480, 480, 480, 480, 480, 1440],
    [480, 480, 480, 480, 480, 1, 481],
    [480, 480, 480, 480, 479, 1, 700],
    [1, 480, 480, 480, 480, 480, 1],
    [450, 450, 450, 450, 450, 150, 900],
    [450, 450, 450, 450, 450, 151, 900],
]

rng = random.Random(40_7_2400_3)
for index in range(150):
    base = rng.choice([300, 360, 400, 420, 450, 480])
    week = [max(1, min(480, base + rng.randint(-60, 60))) for _ in range(6)]
    if index % 4 == 0:
        week[rng.randrange(6)] = rng.randint(1, 480)
    week.append(rng.choice([1, 479, 480, 481, 660, 661, 1440]) if index % 2 else rng.randint(1, 1440))
    weeks.append(week)

problems = []
compare_minutes(call, weeks, lambda index: 3141 + 29 * index, problems)
finish(problems, f"seven-day weeks ok: {len(weeks)} weeks")
