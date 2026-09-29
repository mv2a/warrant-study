"""X: the weekly 40-hour cap on regular time (G2).

Day 7 is always 0 here, so no day can be a seventh consecutive day. Only the three minute
fields are compared. The cases sit on and around 2400 regular minutes, show that daily
overtime and double time do not count toward the 40 hours even when far more than 40 hours
are worked, and that double time never turns into overtime or back. A fixed-seed generator
adds weeks whose regular minutes straddle the cap.
"""

import random

from _cmd import call, finish
from _expect import compare_minutes

weeks = [
    # on and around the cap with plain days
    [480, 480, 480, 480, 480, 0, 0],
    [480, 480, 480, 480, 479, 0, 0],
    [480, 480, 480, 480, 480, 1, 0],
    [400, 400, 400, 400, 400, 400, 0],
    [401, 400, 400, 400, 400, 400, 0],
    [399, 400, 400, 400, 400, 400, 0],
    [480, 480, 480, 480, 480, 480, 0],
    [0, 480, 480, 480, 480, 480, 0],
    [480, 0, 480, 480, 480, 480, 0],
    [470, 470, 470, 470, 470, 71, 0],
    [470, 470, 470, 470, 470, 70, 0],
    [470, 470, 470, 470, 470, 69, 0],
    # long weeks where daily overtime and double time do not count toward 40 hours
    [660, 660, 660, 660, 240, 0, 0],
    [1440, 1440, 480, 0, 0, 0, 0],
    [1440, 1440, 1440, 0, 0, 0, 0],
    [1440, 1440, 1440, 1440, 1440, 0, 0],
    [600, 600, 600, 600, 600, 0, 0],
    [661, 661, 661, 661, 661, 0, 0],
    [700, 700, 700, 700, 479, 0, 0],
    [700, 700, 700, 700, 481, 0, 0],
    [500, 500, 500, 500, 481, 1, 0],
    # past the cap, with daily overtime and double time kept apart
    [600, 600, 600, 600, 600, 600, 0],
    [720, 720, 720, 720, 720, 720, 0],
    [1440, 1440, 1440, 1440, 1440, 1440, 0],
    [480, 480, 480, 480, 480, 1440, 0],
    [1440, 480, 480, 480, 480, 480, 0],
    [0, 900, 900, 900, 900, 900, 0],
    [481, 482, 483, 484, 485, 486, 0],
    [1, 1439, 1, 1439, 1, 1439, 0],
]

rng = random.Random(24_00_7_2026)
POOL = [240, 400, 420, 460, 479, 480, 481, 500, 600, 659, 660, 661, 800, 1200, 1440]
for index in range(150):
    week = [0] * 7
    count = 6 if index % 3 else rng.randint(4, 6)
    for position in rng.sample(range(6), count):
        week[position] = rng.choice(POOL) if rng.random() < 0.4 else rng.randint(300, 1440)
    weeks.append(week)

problems = []
compare_minutes(call, weeks, lambda index: 1250 + 61 * index, problems)
finish(problems, f"weekly cap ok: {len(weeks)} weeks")
