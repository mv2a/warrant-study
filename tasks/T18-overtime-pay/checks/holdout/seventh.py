"""H3: day 7 is paid as a seventh consecutive day exactly when all seven days are worked."""

import random

from _cmd import call, finish
from _model import MINUTE_FIELDS, pick, split

rng = random.Random(7777)
weeks = []
for last in (1, 240, 479, 480, 481, 600, 660, 661, 1440):
    weeks.append([60, 60, 60, 60, 60, 60, last])          # all seven worked
    weeks.append([1, 1, 1, 1, 1, 1, last])
for off in range(6):                                       # one day off: day 7 is ordinary
    for last in (300, 600, 700):
        week = [300] * 6 + [last]
        week[off] = 0
        weeks.append(week)
weeks += [
    [0, 0, 0, 0, 0, 0, 600],
    [480, 480, 480, 480, 480, 480, 0],
    [1440, 1440, 1440, 1440, 1440, 1440, 1440],
]
for _ in range(30):                                        # all seven worked
    weeks.append([rng.randint(1, 1440) for _ in range(7)])
for _ in range(20):                                        # a day off somewhere in days 1-6
    week = [rng.randint(1, 1440) for _ in range(7)]
    week[rng.randrange(6)] = 0
    weeks.append(week)

problems = []
for week in weeks:
    rate = rng.randint(1, 100000)
    status, body = call({"minutes": week, "rate_cents": rate})
    want, got = split(week), pick(body, MINUTE_FIELDS)
    if status != 0 or got != want:
        problems.append(f"{week}: expected regular, overtime, double minutes {want}, got {got!r} (status {status})")

finish(problems, f"seventh-day rule ok: {len(weeks)} weeks")
