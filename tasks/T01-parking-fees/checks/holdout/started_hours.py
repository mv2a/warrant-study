"""H1: parking time is charged at 250 cents per started hour, counted from entry."""

import random

from _cmd import call, finish
from _oracle import clock, request

rng = random.Random(10101)
durations = sorted(
    set(range(16, 131))
    | {k * 60 + d for k in range(2, 7) for d in (-1, 0, 1) if k * 60 + d <= 360}
    | {rng.randint(16, 360) for _ in range(30)}
)
problems = []
for minutes in durations:
    entry = rng.randint(0, 10079 - minutes)
    hours = -(-minutes // 60)
    status, body = call(request(entry, entry + minutes))
    got = body.get("time_cents") if isinstance(body, dict) else None
    if status != 0 or got != 250 * hours:
        problems.append(f"{minutes} minutes from {clock(entry)}: expected time_cents {250 * hours} "
                        f"({hours} started hours), got {got!r} (status {status})")

finish(problems, f"started hours ok: {len(durations)} stays from 16 to 360 minutes")
