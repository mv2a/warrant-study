"""H1: on ordinary days, minutes 1-480 are regular, 481-660 overtime, and the rest double time."""

import random

from _cmd import call, finish
from _model import MINUTE_FIELDS, pick, split

rng = random.Random(1802)
LENGTHS = [1, 59, 479, 480, 481, 540, 659, 660, 661, 700, 719, 720, 721, 780, 1000, 1439, 1440]
weeks = []
for position, length in enumerate(LENGTHS):
    week = [0] * 7
    week[position % 7] = length          # one day per week, on every day of the week in turn
    weeks.append(week)
weeks += [
    [700, 0, 800, 0, 0, 0, 1440],
    [0, 661, 0, 660, 0, 659, 0],
    [1440, 1440, 1440, 1440, 1440, 0, 0],
    [481, 0, 0, 0, 0, 0, 721],
]
for _ in range(45):                        # at most five worked days, so the 40 hours never bind
    week = [0] * 7
    for day in rng.sample(range(7), rng.randint(1, 5)):
        week[day] = rng.choice([rng.randint(1, 1440), rng.randint(470, 490), rng.randint(650, 730)])
    weeks.append(week)

problems = []
for week in weeks:
    rate = rng.randint(1, 100000)
    status, body = call({"minutes": week, "rate_cents": rate})
    want, got = split(week), pick(body, MINUTE_FIELDS)
    if status != 0 or got != want:
        problems.append(f"{week}: expected regular, overtime, double minutes {want}, got {got!r} (status {status})")

finish(problems, f"daily thresholds ok: {len(weeks)} weeks")
