"""X-G1: every started hour of the stay, counted from the minute of entry, costs $2.50.

Covers every stay length from 17 to 360 minutes (1 to 6 started hours, below the daily
cap of G3 and above the free-minute boundary of G2), each at a seeded random start that
stays inside one week, plus stays that cross clock hours or midnight. Only time_cents is
compared, so the overnight and lost-ticket rules do not affect this check.
"""

import random

from _audit import WEEK, got, request, run_many, show, field
from _cmd import finish

rng = random.Random(91_417)
cases = []
for minutes in range(17, 361):
    entry = rng.randint(0, WEEK - 1 - minutes)
    cases.append((entry, entry + minutes))

# Started hours count from the minute of entry, not from the clock hour.
cases += [
    (650, 670),     # Mon 10:50-11:10: 20 minutes is one hour, though it touches two clock hours
    (659, 721),     # Mon 10:59-12:01: 62 minutes is two hours, though it touches three clock hours
    (1439, 1499),   # Mon 23:59-Tue 00:59: 60 minutes across midnight is one hour
    (1439, 1500),   # 61 minutes across midnight is two hours
    (4290, 4410),   # Wed 23:30-Thu 01:30: 120 minutes is two hours
    (4290, 4411),   # 121 minutes is three hours
    (6000, 6060),   # G1's examples at another place in the week: 60, 61 and 120 minutes
    (6000, 6061),
    (6000, 6120),
    (8435, 8795),   # Sat 20:35-Sun 02:35: 360 minutes is six hours (the night does not change the time charge)
    (10019, 10079), # the last hour of the week
]

requests = [request(e, x) for e, x in cases]
problems = []
for req, result in zip(requests, run_many(requests)):
    minutes = req["exit"] - req["entry"]
    want = -(-minutes // 60) * 250
    if field(result, "time_cents") != want:
        problems.append(f"{show(req)} ({minutes} min): expected time_cents {want}, got {got(result, 'time_cents')}")

finish(problems, f"G1 ok: {len(requests)} stays of 17 to 360 minutes charged $2.50 per started hour")
