"""X-G1/G2/G3/C2: seeded random stays across the whole valid domain, every amount exact."""

import random

from _audit import DAYS, amount_problems, call_all, price, refused, request, show
from _cmd import finish

cases = []
for seed, count in ((29092026, 150), (7171717, 150)):
    rng = random.Random(seed)
    while count:
        day = rng.choice(DAYS)
        nights = rng.choice((rng.randint(1, 30), rng.randint(5, 16)))
        band = rng.random()
        if band < 0.25:
            rate = rng.randint(1, 60)
        elif band < 0.8:
            rate = rng.randint(1000, 60000)
        else:
            rate = rng.randint(60001, 2_000_000_000)
        if refused(day, nights):
            continue
        cases.append(request(day, nights, rate))
        count -= 1

problems = []
for req, (status, body) in zip(cases, call_all(cases)):
    want = price(req["check_in"], req["nights"], req["rate_cents"])
    diff = amount_problems(body, want)
    if status != 0 or diff is not None:
        problems.append(f"{show(req)}: expected {want}, got {diff!r} (status {status})")

finish(problems, f"{len(cases)} generated stays priced exactly (seeds 29092026 and 7171717)")
