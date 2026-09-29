"""X-G2: the length-of-stay discount tiers, taken from the whole room charge."""

from _audit import DAYS, call_all, discount_percent, is_number, refused, request, show
from _cmd import finish

# Rates that are multiples of 80: every night price is then a multiple of 20 cents, so 10% and
# 15% of the room charge are whole cents and no rounding is involved.
RATES = [80, 160, 6480, 9920, 12000, 17760, 31040, 88880, 150000]
LENGTHS = [1, 2, 3, 5, 6, 7, 8, 10, 12, 13, 14, 15, 16, 19, 22, 27, 29, 30]

cases = []
for d, day in enumerate(DAYS):
    for i, nights in enumerate(LENGTHS):
        if refused(day, nights):
            continue
        cases.append(request(day, nights, RATES[(d + 3 * i) % len(RATES)]))

problems = []
for req, (status, body) in zip(cases, call_all(cases)):
    nights = req["nights"]
    pct = discount_percent(nights)
    if status != 0 or not isinstance(body, dict) or not is_number(body.get("room_cents")):
        problems.append(f"{show(req)}: expected a priced stay, got {body!r} (status {status})")
        continue
    room = body["room_cents"]
    want = room * pct // 100
    if body.get("discount_cents") != want:
        problems.append(f"{show(req)}: {pct}% of the room charge {room} is {want}, "
                        f"got discount_cents {body.get('discount_cents')!r}")

finish(problems, f"discount tiers ok: 0% below 7 nights, 10% for 7-13, 15% from 14, on {len(cases)} stays")
