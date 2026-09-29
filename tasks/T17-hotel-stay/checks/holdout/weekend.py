"""H1: Friday and Saturday nights carry the 25% surcharge, and the weekdays wrap week after week."""

import random

from _cmd import call, finish
from _model import DAYS, refused_by_min_stay, room

rng = random.Random(1701)
lengths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 20, 21, 22, 27, 28, 29, 30]
cases = []
for day in DAYS:
    for n in lengths:
        if not refused_by_min_stay(day, n):
            # Rates divisible by 4 make the surcharge an exact number of cents, so rounding (C2) plays no part.
            cases.append((day, n, 4 * rng.randint(1, 50000)))
cases += [("fri", 3, 4), ("sat", 3, 4), ("sun", 1, 400000), ("thu", 30, 10000), ("sat", 30, 10000)]

problems = []
for day, n, rate in cases:
    status, body = call({"check_in": day, "nights": n, "rate_cents": rate})
    got = body.get("room_cents") if isinstance(body, dict) else None
    want = room(day, n, rate)
    if status != 0 or got != want:
        problems.append(f"{day}, {n} nights at {rate}: room charge should be {want}, got {got!r} (status {status})")

finish(problems, f"weekend surcharge ok: {len(cases)} stays")
