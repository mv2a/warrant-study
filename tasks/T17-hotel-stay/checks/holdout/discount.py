"""H2: no discount under 7 nights, 10% from 7 to 13 nights, 15% from 14 nights, on the whole room charge."""

import random

from _cmd import call, finish
from _model import DAYS, percent, refused_by_min_stay

rng = random.Random(1314)
cases = []
for n in range(1, 31):
    for day in rng.sample(DAYS, 3):
        if not refused_by_min_stay(day, n):
            # Rates divisible by 80 keep the room charge a multiple of 20, so 10% and 15% are exact cents.
            cases.append((day, n, 80 * rng.randint(1, 2500)))

problems = []
for day, n, rate in cases:
    status, body = call({"check_in": day, "nights": n, "rate_cents": rate})
    if status != 0 or not isinstance(body, dict) or type(body.get("room_cents")) is not int:
        problems.append(f"{day}, {n} nights at {rate}: no price (status {status}, {body!r})")
        continue
    want = body["room_cents"] * percent(n) // 100
    if body.get("discount_cents") != want:
        problems.append(
            f"{day}, {n} nights at {rate}: discount should be {percent(n)}% of the room charge "
            f"{body['room_cents']}, which is {want}, got {body.get('discount_cents')!r}"
        )

finish(problems, f"length-of-stay discount ok: {len(cases)} stays")
