"""X: the whole minute split over the full range of weeks (G1, G2 and G3 together).

A fixed-seed generator draws weeks from the whole valid range: short and long days, days
off anywhere, seven-day weeks with long days, and weeks far past 40 hours. Only the three
minute fields are compared with the split the intent gives.
"""

import random

from _cmd import call, finish
from _expect import compare_minutes

rng = random.Random(10080_18_29)
POOL = [1, 479, 480, 481, 659, 660, 661, 1439, 1440]


def day(r, off_chance):
    roll = r.random()
    if roll < off_chance:
        return 0
    if roll < off_chance + 0.25:
        return r.choice(POOL)
    return r.randint(1, 1440)


weeks = [[1440, 1440, 1440, 1440, 1440, 1440, 1440],
         [540, 540, 540, 540, 540, 540, 540],
         [720, 720, 720, 720, 720, 720, 720],
         [661, 661, 661, 661, 661, 661, 661],
         [1, 1440, 1, 1440, 1, 1440, 1],
         [0, 1440, 1440, 1440, 1440, 1440, 1440]]
for index in range(200):
    off_chance = (0.0, 0.1, 0.35)[index % 3]
    weeks.append([day(rng, off_chance) for _ in range(7)])

problems = []
compare_minutes(call, weeks, lambda index: 1 + (index * 7919) % 100000, problems)
finish(problems, f"full weeks ok: {len(weeks)} weeks")
