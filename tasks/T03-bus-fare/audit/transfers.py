"""X2 (G2): free transfers within 90 minutes of the trip that opened the window, windows never extended."""

import random

from _audit import adult_fare, check_cases, trip
from _cmd import finish

cases = [
    # Exactly 90 minutes after the opener is still a transfer, whatever zones it covers.
    ("90 minutes later, any zones", {"age": 38, "trips": [trip(0, 1, 1), trip(90, 1, 6)]}, [270, 0]),
    ("91 minutes later pays", {"age": 38, "trips": [trip(0, 1, 1), trip(91, 1, 1)]}, [270, 270]),
    ("89 minutes later", {"age": 38, "trips": [trip(1000, 4, 2), trip(1089, 2, 2)]}, [460, 0]),
    ("same minute", {"age": 38, "trips": [trip(700, 3, 4), trip(700, 4, 5), trip(700, 5, 6)]}, [365, 0, 0]),
    ("dearer transfer is still free", {"age": 21, "trips": [trip(300, 2, 2), trip(330, 1, 6)]}, [270, 0]),
    # Transfers never extend the window: the third trip is 60 minutes after the second
    # but 120 after the opener, so it pays and opens a new window at 120.
    ("no extension", {"age": 44, "trips": [trip(0, 5, 5), trip(60, 5, 1), trip(120, 1, 2), trip(210, 2, 6), trip(211, 6, 6)]}, [270, 0, 365, 0, 270]),
    ("no extension, chained", {"age": 44, "trips": [trip(100, 2, 2), trip(160, 2, 3), trip(190, 3, 3), trip(191, 3, 4), trip(281, 4, 4), trip(282, 4, 4)]}, [270, 0, 0, 365, 0, 270]),
    ("ten trips in one window", {"age": 33, "trips": [trip(m, 3, 3) for m in range(10, 101, 10)] + [trip(101, 3, 1)]}, [270] + [0] * 9 + [460]),
    ("end of day, 90 minutes", {"age": 60, "trips": [trip(1349, 6, 6), trip(1439, 6, 1)]}, [270, 0]),
    ("end of day, 91 minutes", {"age": 60, "trips": [trip(1348, 6, 6), trip(1439, 1, 1)]}, [270, 270]),
    ("window from minute 0", {"age": 19, "trips": [trip(0, 2, 3), trip(90, 3, 2), trip(181, 2, 2)]}, [365, 0, 270]),
    ("each window opened by a paid trip", {"age": 55, "trips": [trip(200, 1, 2), trip(291, 2, 3), trip(381, 3, 4), trip(472, 4, 4)]}, [365, 365, 0, 270]),
    # Concession riders transfer the same way.
    ("child transfer", {"age": 9, "trips": [trip(600, 1, 4), trip(690, 4, 1), trip(691, 1, 1)]}, [275, 0, 135]),
    ("senior transfer", {"age": 80, "trips": [trip(60, 1, 2), trip(150, 2, 6), trip(151, 6, 5)]}, [145, 0, 145]),
    ("infant transfer", {"age": 2, "trips": [trip(60, 1, 6), trip(100, 6, 1), trip(500, 1, 6)]}, [0, 0, 0]),
]

# Generated days for a 30-year-old whose window starts are known by construction,
# kept only when the day stays under the adult cap so G4 never interferes.
rng = random.Random(40417)
GAPS = [0, 0, 1, 30, 45, 59, 60, 89, 90, 90, 91, 92, 120, 179, 180, 181, 300]
generated = 0
while generated < 60:
    minute = rng.randint(0, 700)
    trips, fares, opener, paid = [], [], None, 0
    for _ in range(rng.randint(2, 8)):
        start, end = rng.randint(1, 6), rng.randint(1, 6)
        if opener is not None and minute - opener <= 90:
            fares.append(0)
        else:
            opener = minute
            fares.append(adult_fare(start, end))
        trips.append(trip(minute, start, end))
        minute += rng.choice(GAPS)
        if minute > 1439:
            break
    if sum(fares) > 1100:
        continue
    generated += 1
    cases.append((f"seeded day {generated} {[t['board_minute'] for t in trips]}", {"age": 30, "trips": trips}, fares))

finish(check_cases(cases), f"transfers ok: {len(cases)} days")
