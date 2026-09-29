"""X-G4: every 02:00 inside the stay adds $6.00, on top of the time charge and not capped.

A stay includes a 02:00 when entry <= 02:00 < exit. Part A: exact boundaries (entering or
leaving at 02:00, one minute either side), every day of the week, 17-minute stays that
contain a 02:00 (charged) and stays of 14 minutes or less that contain one (free under G2;
15 and 16 minutes are left to G2's own boundary check).
Part B: 200 seeded random stays of 17 minutes or more, half of them placed at a 02:00
boundary. Part C: the fee comes on top: a 4-to-6-hour stay that contains a 02:00 has the
same time_cents as a stay of the same length from the same minute of the hour later that
day that does not, and its total is exactly $6.00 more; the same holds for stays of 20
to 22 hours within one calendar day, where the daily cap binds, so the fee is not
limited by the cap. All stays are inside one week (no wrap, C2).
"""

import random

from _audit import DAY, NIGHT, WEEK, field, got, nights, request, run_many, show
from _cmd import finish

rng = random.Random(77_261)

# Part A: (entry, exit, number of 02:00 moments charged)
exact = [
    (120, 200, 1), (100, 120, 0), (100, 121, 1), (121, 400, 0),
    (119, 136, 1), (120, 137, 1), (103, 120, 0), (104, 121, 1),
    (110, 124, 0), (120, 130, 0), (7310, 7324, 0), (7320, 7337, 1),
    (60, 180, 1), (1320, 1559, 0), (1320, 1560, 0), (1320, 1561, 1),
    (1560, 3000, 1), (1560, 3001, 2), (1559, 3000, 1), (1559, 3001, 2), (1561, 3000, 0),
    (0, WEEK - 1, 7), (120, 8760, 6), (120, 8761, 7), (121, WEEK - 1, 6),
    (8760, WEEK - 1, 1), (8761, WEEK - 1, 0),
]
for day in range(7):
    two = NIGHT + day * DAY
    exact.append((two - 30, two + 30, 1))
    if day < 6:
        exact.append((day * DAY + 180, (day + 1) * DAY + 60, 0))   # 03:00 to 01:00 the next day

# Part B: seeded random stays of 17 minutes or more.
randoms = []
while len(randoms) < 200:
    if rng.random() < 0.5:
        span = rng.choice(((17, 600), (600, 3000), (3000, WEEK - 1)))
        minutes = rng.randint(*span)
        if minutes > WEEK - 1:
            continue
        entry = rng.randint(0, WEEK - 1 - minutes)
        exit = entry + minutes
    else:
        edge = NIGHT + rng.randint(0, 6) * DAY + rng.choice((-1, 0, 1))
        minutes = rng.randint(17, 2 * DAY + 200)
        entry, exit = (edge, edge + minutes) if rng.random() < 0.5 else (edge - minutes, edge)
        if entry < 0 or exit > WEEK - 1:
            continue
    randoms.append((entry, exit))

# Part C: pairs of equal-length stays inside one day, one containing 02:00 and one not,
# starting at the same minute of the hour, so any reading of G1 and G3 charges them alike.
pairs = []
for _ in range(20):
    base = rng.randint(0, 6) * DAY
    minutes = rng.randint(240, 360)
    offset = rng.randint(0, NIGHT)
    with_night = base + offset
    hours_later = rng.randint(8, (DAY - 1 - minutes - offset % 60) // 60)
    without = base + 60 * hours_later + offset % 60
    pairs.append(((with_night, with_night + minutes), (without, without + minutes)))
# Long pairs: the same kind of pair for stays of 20 to 22 hours, where the cap binds.
for day in range(7):
    base = day * DAY
    offset = rng.randint(0, 59)
    minutes = rng.randint(1200, DAY - 1 - NIGHT - 60 - offset)
    later = base + NIGHT + 60 + offset          # 03:00 plus the same minutes past the hour
    pairs.append(((base + offset, base + offset + minutes), (later, later + minutes)))

requests = [request(e, x) for e, x, _ in exact] + [request(e, x) for e, x in randoms]
for a, b in pairs:
    requests += [request(*a), request(*b)]
results = run_many(requests)

problems = []
at = 0
for (entry, exit, count) in exact + [(e, x, nights(e, x - e)) for e, x in randoms]:
    req, result = requests[at], results[at]
    at += 1
    if field(result, "overnight_cents") != count * 600:
        problems.append(f"{show(req)}: expected overnight_cents {count * 600}, got {got(result, 'overnight_cents')}")
for a, b in pairs:
    ra, rb = results[at], results[at + 1]
    qa, qb = requests[at], requests[at + 1]
    at += 2
    ta, tb = field(ra, "time_cents"), field(rb, "time_cents")
    oa, ob = field(ra, "overnight_cents"), field(rb, "overnight_cents")
    sa, sb = field(ra, "total_cents"), field(rb, "total_cents")
    if None in (ta, tb, oa, ob, sa, sb) or oa != 600 or ob != 0 or ta != tb or sa != sb + 600:
        problems.append(f"{show(qa)} vs {show(qb)}: the night should add exactly 600 on top of the same time charge, "
                        f"got time {ta}/{tb}, overnight {oa}/{ob}, total {sa}/{sb}")

finish(problems, f"G4 ok: {len(exact)} boundary stays, {len(randoms)} random stays and {len(pairs)} pairs "
                 f"with and without a night")
