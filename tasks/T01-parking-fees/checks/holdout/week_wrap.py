"""H7: an exit earlier than the entry is in the following week; an exit equal to the entry is zero minutes."""

import random

from _cmd import call, finish
from _oracle import clock, expected, request

FIXED = [
    ((10070, 5, False), {"minutes": 15, "time_cents": 0, "overnight_cents": 0}),
    ((10070, 6, False), {"minutes": 16, "time_cents": 250, "overnight_cents": 0}),
    ((9840, 120, False), {"minutes": 360, "time_cents": 1500, "overnight_cents": 0}),   # leaves Mon 02:00
    ((9840, 121, False), {"minutes": 361, "time_cents": 1600, "overnight_cents": 600}),
    ((3480, 1980, False), {"minutes": 8580, "time_cents": 9600, "overnight_cents": 3600}),
    ((10079, 0, False), {"minutes": 1, "time_cents": 0, "overnight_cents": 0}),
    ((1, 0, False), {"minutes": 10079, "time_cents": 11200, "overnight_cents": 4200}),
    ((0, 0, False), {"minutes": 0, "time_cents": 0, "overnight_cents": 0, "total_cents": 0}),
    ((120, 120, False), {"minutes": 0, "time_cents": 0, "overnight_cents": 0, "total_cents": 0}),
    ((5000, 5000, False), {"minutes": 0, "time_cents": 0, "overnight_cents": 0, "total_cents": 0}),
    ((10079, 10079, False), {"minutes": 0, "time_cents": 0, "overnight_cents": 0, "total_cents": 0}),
    ((5000, 5000, True), {"minutes": 0, "time_cents": 0, "overnight_cents": 0, "total_cents": 2500}),
]
rng = random.Random(70707)
cases = [(args, want) for args, want in FIXED]
for _ in range(40):
    exit_ = rng.randint(0, 10078)
    entry = rng.randint(exit_ + 1, 10079)
    args = (entry, exit_, rng.random() < 0.3)
    cases.append((args, expected(*args)))
problems = []
for (entry, exit_, lost), want in cases:
    status, body = call(request(entry, exit_, lost))
    got = {k: body.get(k) for k in want} if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(f"{clock(entry)} to {clock(exit_)}: expected {want}, got {got!r} (status {status})")

finish(problems, f"week wrap ok: {len(cases)} stays that end next week or at their own entry minute")
