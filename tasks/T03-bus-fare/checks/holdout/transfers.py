"""H2: trips boarding at most 90 minutes after the trip that opened the window are free."""

import random

from _cmd import call, finish

rng = random.Random(30302)
SAME = 270  # an adult trip within one zone


def trip(minute, start=3, end=None):
    return {"board_minute": minute, "from_zone": start, "to_zone": start if end is None else end}


# (label, age, trips, expected fares)
CASES = [
    ("one trip", 30, [trip(0)], [SAME]),
    ("exactly 90 minutes later", 30, [trip(0), trip(90)], [SAME, 0]),
    ("89 minutes later", 30, [trip(100), trip(189)], [SAME, 0]),
    ("91 minutes later", 30, [trip(0), trip(91)], [SAME, SAME]),
    ("the same minute", 30, [trip(600), trip(600)], [SAME, 0]),
    ("window runs from its opener", 30, [trip(0), trip(60), trip(120)], [SAME, 0, SAME]),
    ("transfers do not extend it", 30, [trip(300), trip(345), trip(390), trip(391)], [SAME, 0, 0, SAME]),
    ("a chain of transfers", 30, [trip(0), trip(30), trip(60), trip(90), trip(120), trip(150), trip(180)],
     [SAME, 0, 0, 0, SAME, 0, 0]),
    ("windows one after another", 30, [trip(0), trip(91), trip(181), trip(182), trip(272)], [SAME, SAME, 0, SAME, 0]),
    ("a transfer is free whatever its zones", 30, [trip(500, 2, 2), trip(550, 1, 6), trip(590, 6, 1)], [SAME, 0, 0]),
    ("end of the day, inside", 30, [trip(1349), trip(1439)], [SAME, 0]),
    ("end of the day, outside", 30, [trip(1348), trip(1439)], [SAME, SAME]),
    ("start of the day", 30, [trip(0), trip(0), trip(1)], [SAME, 0, 0]),
    ("a child transfers free", 9, [trip(100), trip(150), trip(190)], [135, 0, 0]),
    ("a child's window runs from its opener", 9, [trip(100), trip(150), trip(191)], [135, 0, 135]),
    ("a senior transfers free", 70, [trip(100, 1, 5), trip(150, 5, 1)], [260, 0]),
]

# Generated adult days: up to 4 paid trips within one zone (4 x 270 stays under the cap).
# Transfers get random zones, since a transfer is free whatever zones it covers.
for number in range(40):
    minute, opened, paid, trips, fares = rng.randint(0, 400), None, 0, [], []
    for _ in range(rng.randint(2, 9)):
        minute += rng.choice([0, 1, 20, 45, 89, 90, 91, 92, 120])
        if minute > 1439:
            break
        if opened is not None and minute - opened <= 90:
            trips.append(trip(minute, rng.randint(1, 6), rng.randint(1, 6)))
            fares.append(0)
        elif paid < 4:
            opened, paid = minute, paid + 1
            trips.append(trip(minute))
            fares.append(SAME)
        else:
            break
    CASES.append((f"generated day {number + 1}", rng.randint(16, 64), trips, fares))

problems = []
for label, age, trips, fares in CASES:
    status, body = call({"age": age, "trips": trips})
    got = body.get("fares_cents") if isinstance(body, dict) else None
    if status != 0 or got != fares:
        minutes = [t["board_minute"] for t in trips]
        problems.append(f"{label} (age {age}, minutes {minutes}): expected {fares}, got {got!r} (status {status})")

finish(problems, f"transfers ok: {len(CASES)} days")
