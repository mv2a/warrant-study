"""X3 (G3): the rider's age picks the fare: free under 5, child 5-15, adult 16-64, senior 65+."""

from _audit import ADULT_TABLE, CHILD_TABLE, SENIOR_TABLE, check_cases, trip
from _cmd import finish

TABLES = {"free": [0] * 6, "child": CHILD_TABLE, "adult": ADULT_TABLE, "senior": SENIOR_TABLE}
AGES = [
    (0, "free"), (1, "free"), (4, "free"),
    (5, "child"), (6, "child"), (12, "child"), (15, "child"),
    (16, "adult"), (41, "adult"), (64, "adult"),
    (65, "senior"), (66, "senior"), (99, "senior"), (120, "senior"),
]
# One single-trip request per age and number of boundaries, alternating direction and zones.
ROUTES = [[(3, 3), (1, 2), (4, 2), (6, 3), (1, 5), (6, 1)],
          [(6, 6), (5, 4), (2, 4), (2, 5), (5, 1), (1, 6)]]

cases = []
for i, (age, kind) in enumerate(AGES):
    for crossed in range(6):
        start, end = ROUTES[i % 2][crossed]
        minute = (137 * (i + 1) + 61 * crossed) % 1440
        cases.append((f"age {age} ({kind}), zone {start} to {end}", {"age": age, "trips": [trip(minute, start, end)]}, [TABLES[kind][crossed]]))

finish(check_cases(cases), f"age bands ok: {len(AGES)} ages x 6 distances")
