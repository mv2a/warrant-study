"""X: the daily thresholds on ordinary days (G1).

Day 7 is always 0 here, so no day can be a seventh consecutive day, and every week has
fewer than 2400 worked minutes, so the weekly cap cannot matter under any reading. Only
the three minute fields are compared. Single days sit on and around the 8-hour and 11-hour
marks on every weekday position; a fixed-seed generator adds mixed weeks.
"""

import random

from _cmd import call, finish
from _expect import compare_minutes

EDGES = [1, 2, 59, 479, 480, 481, 482, 600, 659, 660, 661, 662, 900, 1439, 1440]
weeks = []
for index, worked in enumerate(EDGES):
    week = [0] * 7
    week[index % 6] = worked
    weeks.append(week)

weeks += [
    [481, 481, 0, 0, 0, 0, 0],
    [0, 660, 0, 661, 0, 0, 0],
    [661, 661, 661, 0, 0, 0, 0],
    [1440, 959, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1440, 959, 0],
    [700, 700, 700, 299, 0, 0, 0],
    [479, 479, 479, 479, 479, 0, 0],
    [1, 1, 1, 1, 1, 1, 0],
    [120, 845, 0, 30, 540, 0, 0],
    [0, 0, 1439, 0, 0, 1, 0],
    [0, 480, 480, 480, 0, 481, 0],
    [665, 0, 0, 0, 0, 1000, 0],
]

rng = random.Random(6_60_4_80_18)
POOL = [1, 60, 240, 479, 480, 481, 540, 659, 660, 661, 720, 1439, 1440]
generated = 0
while generated < 130:
    week = [0] * 7
    for position in rng.sample(range(6), rng.randint(1, 6)):
        week[position] = rng.choice(POOL) if rng.random() < 0.45 else rng.randint(1, 1440)
    if sum(week) <= 2399:
        weeks.append(week)
        generated += 1

problems = []
compare_minutes(call, weeks, lambda index: 700 + 37 * index, problems)
finish(problems, f"daily thresholds ok: {len(weeks)} weeks")
