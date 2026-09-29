"""X-G2: a stay of 1 to 15 minutes is free; from 16 minutes the stay is charged from its first minute.

Part A: every length from 1 to 15 minutes at many places in the week, including stays
that contain a 02:00, must have time_cents 0 and overnight_cents 0.
Part B: a 16-minute stay has a time charge, the same as a 17-, 20- or 29-minute stay from
the same start, and the 15 free minutes are not deducted: from the same start, a stay of
60k+1 to 60k+15 minutes costs the same as one of 60k+16 to 60k+29 minutes (both are k+1
started hours; deducting 15 minutes would make the first one hour cheaper). Part B
compares the command with itself, starting on the hour and within one day, so the size of
the hourly charge (G1) and the daily cap (G3) do not affect it.
Zero-minute stays (exit equal to entry) belong to C2 and are not used here.
"""

import random

from _audit import DAY, WEEK, field, got, request, run_many, show
from _cmd import finish

rng = random.Random(30_559)
free = []
for minutes in range(1, 16):
    starts = [0, 106, 113, 119, 120, 1552, 1560, 4439, 7318, WEEK - 1 - minutes]
    starts.append(rng.randint(0, WEEK - 1 - minutes))
    free += [(s, s + minutes) for s in starts]

# Part B groups: stays from one start on the hour whose time charges must all be equal.
groups = []
for _ in range(6):
    start = rng.randint(0, 6) * DAY + 60 * rng.randint(0, 17)          # 00:00 to 17:00, on the hour
    groups.append([(start, start + m) for m in (16, 17, 20, 29)])
for hours in range(1, 6):
    for _ in range(2):
        start = rng.randint(0, 6) * DAY + 60 * rng.randint(0, 17)
        short = 60 * hours + rng.randint(1, 15)
        long_ = 60 * hours + rng.randint(16, 29)
        groups.append([(start, start + short), (start, start + long_)])
groups.append([(4380, 4441), (4380, 4455), (4380, 4456), (4380, 4469)])   # 61, 75, 76 and 89 minutes

requests = [request(e, x) for e, x in free]
for group in groups:
    requests += [request(e, x) for e, x in group]
results = run_many(requests)

problems = []
for req, result in zip(requests, results[:len(free)]):
    t, o = field(result, "time_cents"), field(result, "overnight_cents")
    if t != 0 or o != 0:
        problems.append(f"{show(req)} ({req['exit'] - req['entry']} min, free): expected time_cents 0 and "
                        f"overnight_cents 0, got {got(result, 'time_cents')}, {got(result, 'overnight_cents')}")
at = len(free)
for group in groups:
    charges = [field(results[at + i], "time_cents") for i in range(len(group))]
    reqs = requests[at:at + len(group)]
    at += len(group)
    lengths = [r["exit"] - r["entry"] for r in reqs]
    if None in charges or len(set(charges)) != 1 or (16 in lengths and charges[0] <= 0):
        problems.append(f"from {show(reqs[0]).split(' exit')[0]}: stays of {lengths} minutes are the same number of "
                        f"started hours and should have one positive time charge, got {charges}")

finish(problems, f"G2 ok: {len(free)} free stays of 1 to 15 minutes and {len(groups)} groups charged from the first minute")
