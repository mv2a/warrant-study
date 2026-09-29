"""H2: regular time is capped at 2400 minutes a week; the excess, and only it, becomes overtime."""

import random

from _cmd import call, finish
from _model import MINUTE_FIELDS, pick, split

rng = random.Random(2400)
weeks = [
    [480, 480, 480, 480, 480, 0, 0],       # exactly 40 hours: nothing moves
    [400, 400, 400, 400, 400, 400, 0],     # exactly 40 hours over six days
    [480, 480, 480, 480, 480, 1, 0],       # one minute past 40 hours
    [300, 480, 480, 480, 480, 480, 0],     # the 40 hours run out partway through day 6
    [480, 480, 480, 480, 300, 480, 0],
    [0, 480, 480, 480, 480, 479, 2],       # day 1 off, so day 7 is an ordinary day
    [410, 410, 410, 410, 410, 410, 0],
    [600, 600, 600, 600, 600, 600, 0],     # daily overtime stays overtime
    [720, 720, 720, 720, 720, 720, 0],     # double time stays double time
    [1440, 1440, 1440, 1440, 1440, 1440, 0],
    [0, 1440, 1440, 1440, 1440, 1440, 1440],
    [480, 480, 480, 480, 480, 480, 600],   # seventh-day minutes never count toward the 40 hours
    [1, 480, 480, 480, 480, 480, 1440],
    [540, 540, 540, 540, 540, 60, 0],      # daily overtime does not count toward the 40 hours
    [470, 470, 470, 470, 470, 60, 0],
]
for _ in range(50):
    week = [rng.choice([rng.randint(300, 600), rng.randint(1, 1440)]) for _ in range(7)]
    if rng.random() < 0.6:
        week[rng.randrange(7)] = 0
    weeks.append(week)

problems = []
for week in weeks:
    rate = rng.randint(1, 100000)
    status, body = call({"minutes": week, "rate_cents": rate})
    want, got = split(week), pick(body, MINUTE_FIELDS)
    if status != 0 or got != want:
        problems.append(f"{week}: expected regular, overtime, double minutes {want}, got {got!r} (status {status})")

finish(problems, f"weekly threshold ok: {len(weeks)} weeks")
