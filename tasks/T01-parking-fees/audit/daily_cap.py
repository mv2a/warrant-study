"""X-G3: the time charge is capped at $16.00 per 24-hour period counted from entry.

Part A, one period: a stay of 421 to 1439 minutes (8 or more started hours) has
time_cents exactly 1600, including stays that cross midnight; a stay of 361 to 420
minutes costs what the command charges for the same stay one hour shorter plus one more
hour, capped at 1600 (so 1600 with the G1 rate). Lengths of 30 minutes past the hour are
left out of that step, so that rounding half hours (a G1 fault) cannot fail this check.
Part B, several periods: a stay of k full 24-hour periods plus r leftover minutes costs
k x 1600 plus, for r of 30 or more, what the command charges for the leftover stay alone
(the same minutes, from entry + k x 24 hours), and for r of 1 to 29, one started hour
(what it charges for 20 minutes from the same place): the free minutes of G2 do not apply
to the leftover. Part B compares the command with itself, so the hourly charge (G1) is
not tested here. All stays are inside one week (no wrap, C2); only time_cents is compared.
"""

import random

from _audit import DAY, WEEK, field, got, request, run_many, show
from _cmd import finish

rng = random.Random(62_083)
requests = []
plan = []   # (index of the stay, kind, helper indices, k)


def add(req):
    requests.append(req)
    return len(requests) - 1


def single(entry, minutes):
    stay = add(request(entry, entry + minutes))
    if minutes <= 420:
        helpers = (add(request(entry, entry + minutes - 60)), add(request(entry, entry + minutes - 120)))
        plan.append((stay, "step", helpers, 0))
    else:
        plan.append((stay, "cap", (), 0))


def several(entry, minutes):
    full, rest = divmod(minutes, DAY)
    stay = add(request(entry, entry + minutes))
    start = entry + full * DAY
    if rest == 0:
        plan.append((stay, "full", (), full))
    elif rest < 30:
        plan.append((stay, "few", (add(request(start, start + 20)),), full))
    else:
        plan.append((stay, "rest", (add(request(start, start + rest)),), full))


# Part A
for minutes in [361, 362, 375, 391, 400, 419, 420] + rng.sample([m for m in range(363, 419) if m % 60 != 30], 8):
    single(rng.randint(0, WEEK - 1 - minutes), minutes)
for minutes in [421, 450, 480, 481, 600, 719, 720, 721, 1000, 1379, 1380, 1438, 1439] + rng.sample(range(422, 1439), 40):
    single(rng.randint(0, WEEK - 1 - minutes), minutes)
for entry, exit in [(1380, 1860), (600, 1620), (1080, 1560), (8200, 8700), (2860, 3320)]:
    single(entry, exit - entry)        # Mon 23:00-Tue 07:00, Mon 10:00-Tue 03:00, ... across midnight

# Part B: entries at minute 0 to 30 of an hour, so leftovers under 30 minutes and the
# 20-minute comparison stay lie within one clock hour.
LEFTOVERS = (0, 1, 7, 15, 16, 29, 30, 59, 60, 61, 300, 360, 361, 420, 421, 719, 1000, 1380, 1439)
for full in range(1, 7):
    for rest in LEFTOVERS:
        minutes = full * DAY + rest
        if minutes <= WEEK - 1:
            entry = rng.randint(0, (WEEK - 1 - minutes) // 60) * 60 + rng.randint(0, 30)
            if entry + minutes > WEEK - 1:
                entry = WEEK - 1 - minutes - (WEEK - 1 - minutes) % 60
            several(entry, minutes)
for entry, exit in [(1200, 2640), (0, 1441), (1441, 2896), (5000, 7895), (100, 4420), (2900, 4700),
                    (2900, 4701), (4000, 6000), (0, WEEK - 1), (1380, 4380)]:
    several(entry, exit - entry)
for _ in range(40):
    minutes = rng.randint(DAY + 16, WEEK - 1)
    if minutes % DAY < 30:
        continue
    several(rng.randint(0, WEEK - 1 - minutes), minutes)

results = run_many(requests)
problems = []
for stay, kind, helpers, full in plan:
    req, result = requests[stay], results[stay]
    minutes = req["exit"] - req["entry"]
    h = [field(results[i], "time_cents") for i in helpers]
    if None in h:
        problems.append(f"{show(requests[helpers[h.index(None)]])}: no time_cents to compare with ({got(results[helpers[h.index(None)]])})")
        continue
    if kind == "cap":
        want, why = 1600, "8 or more started hours in one period"
    elif kind == "step":
        want, why = min(h[0] + (h[0] - h[1]), 1600), f"{minutes - 60} minutes ({h[0]}) plus one more hour ({h[0] - h[1]}), capped"
    elif kind == "full":
        want, why = full * 1600, f"{full} full periods"
    elif kind == "few":
        want, why = full * 1600 + h[0], f"{full} full periods plus one started hour ({h[0]})"
    else:
        want, why = full * 1600 + h[0], f"{full} full periods plus the leftover stay's {h[0]}"
    if field(result, "time_cents") != want:
        problems.append(f"{show(req)} ({minutes} min): expected time_cents {want} ({why}), got {got(result, 'time_cents')}")

finish(problems, f"G3 ok: {len(plan)} stays of 361 minutes or more capped at $16.00 per 24 hours from entry")
