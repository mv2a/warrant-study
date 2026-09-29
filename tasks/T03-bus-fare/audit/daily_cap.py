"""X4 (G4): the daily cap (1100 adult, 550 child, 440 senior) after transfers and concessions."""

import random

from _audit import CAP_CENTS, band, check_cases, price, trip
from _cmd import finish


def far_apart(age, routes, first=0, gap=100):
    """A day of trips each more than 90 minutes after the one before, so no transfers."""
    return {"age": age, "trips": [trip(first + k * gap, s, e) for k, (s, e) in enumerate(routes)]}


cases = [
    # Adult: the trip that crosses the cap pays only what is left, then everything is free.
    ("adult, partial then free", far_apart(45, [(1, 6), (6, 3), (3, 3), (1, 6)]), [745, 355, 0, 0]),
    ("adult, one-zone trips", far_apart(31, [(2, 2)] * 6), [270, 270, 270, 270, 20, 0]),
    ("adult, age 64 boundary", far_apart(64, [(1, 4), (4, 1), (2, 2)]), [555, 545, 0]),
    ("adult, age 16 boundary", far_apart(16, [(6, 2), (2, 6), (5, 5), (1, 2)]), [650, 450, 0, 0]),
    # The cap counts amounts charged, after transfers: a free transfer uses none of it.
    ("adult, transfers do not count", {"age": 45, "trips": [trip(0, 1, 6), trip(60, 6, 1), trip(200, 1, 3), trip(230, 3, 6), trip(500, 2, 2)]}, [745, 0, 355, 0, 0]),
    ("adult, under cap with transfers", {"age": 27, "trips": [trip(0, 1, 6), trip(80, 6, 1), trip(170, 1, 1), trip(250, 1, 6)]}, [745, 0, 270, 0]),
    # Child cap 550, applied to child fares.
    ("child, partial", far_apart(12, [(1, 6), (6, 1), (1, 1)], gap=91), [370, 180, 0]),
    ("child, exactly the cap", far_apart(5, [(1, 4), (4, 1), (2, 2), (1, 6)], gap=200), [275, 275, 0, 0]),
    ("child, small remainder", far_apart(15, [(3, 3)] * 6), [135, 135, 135, 135, 10, 0]),
    ("child, cap reached far below 1100", far_apart(8, [(1, 2), (2, 3), (3, 4), (1, 3)]), [180, 180, 180, 10]),
    # Senior cap 440, applied to senior fares.
    ("senior, partial", far_apart(65, [(1, 6), (6, 1), (3, 3)], gap=91), [295, 145, 0]),
    ("senior, exactly the cap", far_apart(70, [(1, 4), (4, 1), (1, 2)], gap=91), [220, 220, 0]),
    ("senior, small remainder", far_apart(120, [(4, 4)] * 6), [105, 105, 105, 105, 20, 0]),
    ("senior, transfers do not count", {"age": 77, "trips": [trip(10, 1, 6), trip(20, 6, 1), trip(101, 2, 2), trip(192, 5, 3), trip(400, 3, 3)]}, [295, 0, 105, 40, 0]),
    # After the cap is reached, even a trip opening a new window at the end of the day is free.
    ("adult, late trips after cap", {"age": 50, "trips": [trip(0, 1, 6), trip(91, 6, 1), trip(1300, 3, 3), trip(1439, 1, 6)]}, [745, 355, 0, 0]),
    # Riders under 5 are never charged, however many trips.
    ("infant, many trips", far_apart(4, [(1, 6), (6, 1)] * 5, gap=120), [0] * 10),
]

# Generated days with many far-apart trips, so the cap binds for every paying band.
rng = random.Random(730291)
ages = [0, 3, 5, 9, 15, 16, 30, 64, 65, 72, 120]
for n in range(66):
    age = ages[n % len(ages)]
    minute, trips, wanted = rng.randint(0, 60), [], rng.randint(4, 12)
    while minute <= 1439 and len(trips) < wanted:
        trips.append(trip(minute, rng.randint(1, 6), rng.randint(1, 6)))
        minute += rng.choice([91, 95, 120, 150, 30, 0])
    fares = price(age, trips)
    kind = band(age)
    assert sum(fares) <= CAP_CENTS.get(kind, 0)
    cases.append((f"seeded day {n + 1}, age {age}", {"age": age, "trips": trips}, fares))

problems = check_cases(cases)
finish(problems, f"daily cap ok: {len(cases)} days")
