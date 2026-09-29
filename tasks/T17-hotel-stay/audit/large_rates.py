"""X-C2 (large amounts): exact whole-cent arithmetic for very large nightly rates."""

from _audit import amount_problems, call_all, price, request, show
from _cmd import finish

RATES = [2**31 + 1, 10**12 + 2, 2**53 + 1, 2**53 + 2, 3 * 10**15 + 7, 987654321987654321]
STAYS = [("fri", 3), ("mon", 7), ("thu", 14), ("sat", 30)]

cases = [request(day, nights, RATES[(i + j) % len(RATES)])
         for i, (day, nights) in enumerate(STAYS) for j in range(3)]

problems = []
for req, (status, body) in zip(cases, call_all(cases)):
    want = price(req["check_in"], req["nights"], req["rate_cents"])
    diff = amount_problems(body, want)
    if status != 0 or diff is not None:
        problems.append(f"{show(req)}: expected {want}, got {diff!r} (status {status})")

finish(problems, f"large rates ok: {len(cases)} stays with rates from 2**31 to about 10**18 cents priced exactly")
