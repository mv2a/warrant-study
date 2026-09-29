"""H4: every 02:00 inside the stay adds 600 cents, entering at 02:00 counts and leaving at 02:00 doesn't."""

import random

from _cmd import call, finish
from _oracle import clock, expected, request

FIXED = [
    (1560, 1620, 1),    # enters Tue 02:00 exactly
    (1561, 1620, 0),    # enters Tue 02:01
    (1500, 1560, 0),    # leaves Tue 02:00 exactly
    (1500, 1561, 1),    # leaves Tue 02:01
    (1380, 1530, 0),    # Mon 23:00 to Tue 01:30 crosses midnight, not 02:00
    (119, 136, 1),      # 17 minutes over Mon 02:00
    (0, 120, 0),
    (60, 3000, 2),      # Mon 02:00 and Tue 02:00, but it leaves Wed 02:00 exactly
    (60, 3001, 3),
    (8400, 9180, 1),    # Sat 20:00 to Sun 09:00
    (8760, 10079, 1),   # enters Sun 02:00 exactly
    (1500, 2939, 1),    # a capped 24-hour period still pays its night
    (120, 10079, 7),
    (121, 10079, 6),
    (0, 10079, 7),      # seven nights on top of the capped time charge
]
rng = random.Random(40404)
cases = [(e, x) for e, x, _ in FIXED]
for _ in range(80):
    minutes = rng.choice((rng.randint(16, 600), rng.randint(16, 3000), rng.randint(16, 10079)))
    entry = rng.randint(0, 10079 - minutes)
    cases.append((entry, entry + minutes))
nights = {(e, x): n for e, x, n in FIXED}
problems = []
for entry, exit_ in cases:
    want = expected(entry, exit_, False)
    if (entry, exit_) in nights:
        assert want["overnight_cents"] == 600 * nights[(entry, exit_)], (entry, exit_)
    status, body = call(request(entry, exit_))
    got = (body.get("overnight_cents"), body.get("total_cents")) if isinstance(body, dict) else None
    if status != 0 or got != (want["overnight_cents"], want["total_cents"]):
        problems.append(f"{clock(entry)} to {clock(exit_)}: expected (overnight, total) "
                        f"{(want['overnight_cents'], want['total_cents'])}, got {got!r} (status {status})")

finish(problems, f"overnight ok: {len(cases)} stays, {len(FIXED)} of them at the 02:00 boundaries")
