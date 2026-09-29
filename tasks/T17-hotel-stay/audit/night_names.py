"""X-G1: the room charge names every night by the weekday it begins on, across all weeks."""

from _audit import DAYS, call_all, price, refused, request, show
from _cmd import finish

# Rates that are multiples of 4, so 25% is a whole number of cents and rounding plays no part.
RATES = [4, 8, 12, 396, 7004, 11112, 15996, 20000, 33332, 250004, 999996, 4000000]

cases = []
for d, day in enumerate(DAYS):
    for nights in range(1, 31):
        if refused(day, nights):
            continue
        cases.append(request(day, nights, RATES[(d * 5 + nights) % len(RATES)]))

problems = []
for req, (status, body) in zip(cases, call_all(cases)):
    want = price(req["check_in"], req["nights"], req["rate_cents"])["room_cents"]
    got = body.get("room_cents") if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(f"{show(req)}: expected room_cents {want}, got {got!r} (status {status})")

finish(problems, f"room charge ok for all {len(cases)} check-in day and length pairs from 1 to 30 nights")
