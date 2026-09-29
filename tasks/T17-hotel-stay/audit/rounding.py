"""X-C2: whole-cent arithmetic: per-night surcharge rounded half up, discount rounded down."""

from fractions import Fraction

from _audit import DAYS, amount_problems, call_all, discount_percent, price, request, show
from _cmd import finish

cases = []

# (a) The surcharge is rounded night by night: small rates where 25% has a quarter, half or
# three-quarter cent left over, on stays with one, two or more weekend nights.
for rate in range(1, 25):
    for day, nights in (("fri", 1), ("fri", 3), ("wed", 6)):
        cases.append(request(day, nights, rate))
for rate in (1002, 1010, 12002, 12010, 40018, 99998, 100001, 100003, 7777, 6):
    for day, nights in (("thu", 4), ("fri", 6), ("sat", 5)):
        cases.append(request(day, nights, rate))
for rate in (1, 2, 3, 5, 6, 10, 14):
    for day, nights in (("fri", 14), ("fri", 30), ("thu", 9)):
        cases.append(request(day, nights, rate))

# (b) The discount is rounded down even when the fraction is a half cent or more.
for i, nights in enumerate((7, 9, 11, 13, 14, 17, 23, 30)):
    day = DAYS[(3 * i + 1) % 7]
    wanted = {"at least half": 2, "under half": 1}
    rate = 3001 + 97 * i
    while any(wanted.values()):
        room = price(day, nights, rate)["room_cents"]
        frac = Fraction(room * discount_percent(nights), 100) % 1
        kind = "at least half" if frac >= Fraction(1, 2) else "under half" if frac > 0 else None
        if kind and wanted[kind]:
            wanted[kind] -= 1
            cases.append(request(day, nights, rate))
        rate += 1

problems = []
for req, (status, body) in zip(cases, call_all(cases)):
    want = price(req["check_in"], req["nights"], req["rate_cents"])
    diff = amount_problems(body, want)
    if status != 0 or diff is not None:
        problems.append(f"{show(req)}: expected {want}, got {diff!r} (status {status})")

finish(problems, f"rounding ok on {len(cases)} stays: surcharge per night half up, discount down")
