"""X12 (G1, G2, G3, G4, C1): seeded random days priced against a model written from intent.md."""

import random

from _audit import CAP_CENTS, band, check_cases, price, trip
from _cmd import finish

BOUNDARY_AGES = [0, 4, 5, 15, 16, 64, 65, 120]
GAPS = [0, 1, 17, 44, 89, 90, 91, 133, 181, 240, 400]

cases = []
for seed, count in ((318877, 110), (2046061, 110)):
    rng = random.Random(seed)
    for n in range(count):
        age = rng.choice(BOUNDARY_AGES) if rng.random() < 0.4 else rng.randint(0, 120)
        minute, trips = rng.randint(0, 900), []
        for _ in range(rng.randint(0, 15)):
            if minute > 1439:
                break
            trips.append(trip(minute, rng.randint(1, 6), rng.randint(1, 6)))
            minute += rng.choice(GAPS)
        fares = price(age, trips)
        assert sum(fares) <= CAP_CENTS.get(band(age), 0)
        cases.append((f"seed {seed} day {n + 1} (age {age}, {len(trips)} trips)", {"age": age, "trips": trips}, fares))

finish(check_cases(cases), f"generated days ok: {len(cases)} days from 2 seeds")
