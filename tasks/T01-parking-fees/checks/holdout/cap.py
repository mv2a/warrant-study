"""H3: the time charge is capped at 1600 cents for each 24-hour period counted from entry."""

import random

from _cmd import call, finish
from _oracle import clock, expected, request

FIXED = {
    360: 1500, 361: 1600, 419: 1600, 420: 1600, 421: 1600, 1439: 1600, 1440: 1600,
    1441: 1850, 1455: 1850, 1500: 1850, 1501: 2100, 1800: 3100, 1801: 3200, 2879: 3200,
    2880: 3200, 2881: 3450, 3240: 4700, 3241: 4800, 4320: 4800, 5000: 6400, 8640: 9600,
    8641: 9850, 9000: 11100, 9001: 11200, 10079: 11200,
}
rng = random.Random(30303)
cases = [(m, rng.randint(0, 10079 - m), t) for m, t in FIXED.items()]
for _ in range(60):
    minutes = rng.randint(16, 10079)
    entry = rng.randint(0, 10079 - minutes)
    cases.append((minutes, entry, expected(entry, entry + minutes, False)["time_cents"]))
problems = []
for minutes, entry, time_cents in cases:
    status, body = call(request(entry, entry + minutes))
    got = body.get("time_cents") if isinstance(body, dict) else None
    if status != 0 or got != time_cents:
        problems.append(f"{minutes} minutes from {clock(entry)}: expected time_cents {time_cents}, "
                        f"got {got!r} (status {status})")

finish(problems, f"daily cap ok: {len(cases)} stays up to 10079 minutes")
