"""H10: 150 seeded random stays across the week get exactly the fee the tariff gives."""

import random

from _cmd import call, finish
from _oracle import FIELDS, clock, expected, request

rng = random.Random(101010)
cases = []
for _ in range(150):
    entry = rng.randint(0, 10079)
    shape = rng.random()
    if shape < 0.25:
        exit_ = (entry + rng.randint(0, 30)) % 10080          # around the free 15 minutes
    elif shape < 0.55:
        exit_ = (entry + rng.randint(300, 1600)) % 10080      # around the daily cap
    else:
        exit_ = rng.randint(0, 10079)                         # anything, often next week
    cases.append((entry, exit_, rng.random() < 0.25))
problems = []
for entry, exit_, lost in cases:
    want = expected(entry, exit_, lost)
    status, body = call(request(entry, exit_, lost))
    got = {f: body.get(f) for f in FIELDS} if isinstance(body, dict) else body
    if status != 0 or got != want:
        problems.append(f"{clock(entry)} to {clock(exit_)}{' lost ticket' if lost else ''}: "
                        f"expected {want}, got {got!r} (status {status})")

finish(problems, f"random stays ok: {len(cases)} stays match the tariff exactly")
