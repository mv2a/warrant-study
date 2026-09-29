"""H3: city tax of 275 cents on each of the first 10 nights, charged in full even when the room is discounted."""

import random

from _cmd import call, finish
from _model import DAYS, refused_by_min_stay, tax

rng = random.Random(275)
cases = []
for n in range(1, 31):
    day = rng.choice([d for d in DAYS if not refused_by_min_stay(d, n)])
    cases.append((day, n, rng.randint(1, 90000)))
cases += [("mon", 10, 1), ("mon", 11, 1), ("wed", 9, 50000), ("sun", 30, 1)]

problems = []
for day, n, rate in cases:
    status, body = call({"check_in": day, "nights": n, "rate_cents": rate})
    if status != 0 or not isinstance(body, dict):
        problems.append(f"{day}, {n} nights at {rate}: no price (status {status}, {body!r})")
        continue
    want = tax(n)
    room, discount, total = body.get("room_cents"), body.get("discount_cents"), body.get("total_cents")
    if body.get("tax_cents") != want:
        problems.append(f"{n} nights: city tax should be {want}, got {body.get('tax_cents')!r}")
    elif all(type(v) is int for v in (room, discount, total)) and total - (room - discount) != want:
        problems.append(
            f"{n} nights at {rate}: the total {total} should add the full city tax {want} "
            f"to the discounted room charge {room - discount}"
        )

finish(problems, f"city tax ok: {len(cases)} stays")
