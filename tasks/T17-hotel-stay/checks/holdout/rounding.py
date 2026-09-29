"""H6: whole cents; per-night surcharge rounded to nearest with halves up; discount rounded down; totals add up."""

import random

from _cmd import call, finish
from _model import DAYS, percent, refused_by_min_stay, surcharge

rng = random.Random(4025)
problems = []

# Surcharge rounding, night by night. Short stays keep the weekday arithmetic trivial.
# Rate 1001: 250.25 per night rounds to 250 (rounding the two nights together would give 501).
# Rate 1002: 250.5 rounds up to 251. Rate 1003: 250.75 rounds to 251. Rates 2 more than a multiple
# of 8 are where rounding halves to even goes wrong.
rates = [1, 2, 3, 4, 5, 6, 7, 8, 10, 1001, 1002, 1003, 1006, 1010, 99998, 99999]
rates += [8 * rng.randint(1, 20000) + 2 for _ in range(12)] + [rng.randint(1, 200000) for _ in range(12)]
for rate in rates:
    for day, n in (("fri", 3), ("thu", 4), ("fri", 1)):
        status, body = call({"check_in": day, "nights": n, "rate_cents": rate})
        got = body.get("room_cents") if isinstance(body, dict) else None
        weekend = 1 if n == 1 else 2
        want = n * rate + weekend * surcharge(rate)
        if status != 0 or got != want:
            problems.append(
                f"{day}, {n} nights at {rate}: each weekend night's surcharge is {surcharge(rate)}, "
                f"so the room charge should be {want}, got {got!r} (status {status})"
            )
            break

# Discount rounding: always down, taken from the reported room charge.
for _ in range(40):
    n = rng.choice([8, 9, 10, 11, 12, 13, 14, 17, 21, 25, 30])
    day = rng.choice(DAYS)
    rate = rng.randint(1, 150000)
    status, body = call({"check_in": day, "nights": n, "rate_cents": rate})
    if status != 0 or not isinstance(body, dict) or type(body.get("room_cents")) is not int:
        problems.append(f"{day}, {n} nights at {rate}: no price (status {status}, {body!r})")
        continue
    exact = body["room_cents"] * percent(n) / 100
    want = body["room_cents"] * percent(n) // 100
    if body.get("discount_cents") != want:
        problems.append(f"{n} nights, room {body['room_cents']}: {percent(n)}% is {exact}, so the discount should be {want}, got {body.get('discount_cents')!r}")

# Whole cents, and the total is room minus discount plus tax, for every kind of stay.
for _ in range(40):
    day = rng.choice(DAYS)
    n = rng.randint(1, 30)
    if refused_by_min_stay(day, n):
        n += 2
    rate = rng.randint(1, 300000)
    status, body = call({"check_in": day, "nights": n, "rate_cents": rate})
    amounts = [body.get(f) for f in ("room_cents", "discount_cents", "tax_cents", "total_cents")] if isinstance(body, dict) else None
    if status != 0 or amounts is None or not all(type(a) is int and a >= 0 for a in amounts):
        problems.append(f"{day}, {n} nights at {rate}: amounts should be whole, non-negative cents, got {body!r} (status {status})")
        continue
    room, discount, tax, total = amounts
    if total != room - discount + tax:
        problems.append(f"{day}, {n} nights at {rate}: total {total} should be {room} - {discount} + {tax} = {room - discount + tax}")

finish(problems, f"rounding and arithmetic ok: {len(rates)} rates, 80 more stays")
