"""X-C2: an exit before the entry is in the following week; an exit equal to the entry is zero minutes.

Part A: a stay with exit equal to entry has minutes 0, time_cents 0 and overnight_cents 0.
Part B: for a stay into the following week, minutes is 10080 - entry + exit, and when the
same stay fits inside one week after moving it back by whole days, both answers are equal
field for field (moving by whole days keeps every 02:00 in place, so this tests that the
02:00 moments of the following week count, including an exit at exactly 02:00).
Part C: for a stay too long to move (over six days), minutes is 10080 - entry + exit and
overnight_cents counts the 02:00 moments of both weeks: where a stay of the same length
with the same number of 02:00 moments exists inside one week, overnight_cents equals the
fee for that stay, or the fee for the part from the entry to the end of the week plus the
fee for the part from Monday 00:00 to the exit. Comparing with stays inside one week keeps this check about the wrap alone;
the time charge depends only on minutes and is left to G1 to G3.
"""

import random

from _audit import DAY, NIGHT, WEEK, field, got, nights, request, run_many, show, stay_minutes
from _cmd import finish

rng = random.Random(55_127)

zero = [0, 120, 1560, 5040, 8760, WEEK - 1, rng.randint(0, WEEK - 1), rng.randint(0, WEEK - 1)]

wraps = [(9000, 120), (9000, 121), (9000, 119), (10070, 130), (10075, 5), (10070, 6), (10064, 0),
         (10065, 0), (WEEK - 1, 0), (8761, 121), (8760, 120), (8760, 119), (9840, 510), (10050, 120),
         (5000, 4000), (1, 0), (WEEK - 1, WEEK - 2), (100, 50), (1439, 1438), (1300, 200), (8000, 1600)]
while len(wraps) < 150:
    kind = rng.random()
    if kind < 0.5:
        entry, exit = rng.randint(1, WEEK - 1), None
        exit = rng.randint(0, entry - 1)
    elif kind < 0.7:
        exit = NIGHT + rng.randint(0, 6) * DAY + rng.choice((-1, 0, 1))
        entry = rng.randint(exit + 1, WEEK - 1)
    elif kind < 0.85:
        entry = NIGHT + rng.randint(0, 6) * DAY + rng.choice((-1, 0, 1))
        exit = rng.randint(0, entry - 1)
    else:
        entry = rng.randint(1500, WEEK - 1)
        exit = entry - rng.randint(1, 1400)
    wraps.append((entry, exit))

requests = [request(e, e) for e in zero]
plan = []
for e, x in wraps:
    minutes = stay_minutes(e, x)
    phase = e % DAY
    if phase + minutes <= WEEK - 1:
        shifts = range(phase, WEEK - minutes, DAY)
        start = rng.choice(list(shifts))
        plan.append(("B", e, x, minutes, len(requests), start))
        requests += [request(e, x), request(start, start + minutes)]
    else:
        count = nights(e, minutes)
        same = [s for s in range(0, WEEK - minutes) if nights(s, minutes) == count]
        start = rng.choice(same) if same else None
        plan.append(("C", e, x, minutes, len(requests), start))
        requests += [request(e, x), request(e, WEEK - 1), request(0, x)]
        if start is not None:
            requests.append(request(start, start + minutes))
results = run_many(requests)

problems = []
for i, e in enumerate(zero):
    status, body = results[i]
    if any(field(results[i], f) != 0 for f in ("minutes", "time_cents", "overnight_cents")):
        problems.append(f"{show(requests[i])}: expected a zero-minute stay with no charges, got status {status} and {body!r}")

for kind, e, x, minutes, at, start in plan:
    req, (status, body) = requests[at], results[at]
    if field(results[at], "minutes") != minutes:
        problems.append(f"{show(req)}: expected minutes {minutes}, got {got(results[at], 'minutes')}")
        continue
    if kind == "B":
        s_status, s_body = results[at + 1]
        if s_status != 0 or s_body != body:
            problems.append(f"{show(req)}: expected the same answer as {show(requests[at + 1])} ({s_body!r}), got {body!r}")
        continue
    if start is None:
        continue        # only minutes is checked when no comparison stay has the same nights
    to_end = field(results[at + 1], "overnight_cents") if e < WEEK - 1 else 0
    from_start = field(results[at + 2], "overnight_cents") if x > 0 else 0
    options = [field(results[at + 3], "overnight_cents")]
    if to_end is not None and from_start is not None:
        options.append(to_end + from_start)
    got_nights = field(results[at], "overnight_cents")
    if got_nights is None or got_nights not in options:
        problems.append(f"{show(req)}: expected overnight_cents counting the 02:00 moments of both weeks "
                        f"({' or '.join(map(str, options))}), got {got_nights!r}")

moved = sum(1 for p in plan if p[0] == "B")
finish(problems, f"C2 ok: {len(zero)} zero-minute stays, {moved} wrapped stays matched to moved ones and "
                 f"{len(plan) - moved} long wrapped stays matched by parts")
