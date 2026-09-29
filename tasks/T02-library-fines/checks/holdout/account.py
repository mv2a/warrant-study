"""H4: the total is the sum of item fines capped at 2500; item fines are reported before the account cap (G4)."""

import random

from _cmd import call, finish
from _model import ACCOUNT_CAP, TYPES, item, item_fine

rng = random.Random(250025)
problems = []

FIXED = [
    [("dvd", 40), ("dvd", 50)],                      # 2000 + 2000 = 4000
    [("dvd", 23), ("book", 23)],                     # 2000 + 500 = 2500, exactly the cap
    [("dvd", 23), ("book", 24)],                     # 2000 + 525 = 2525
    [("dvd", 23), ("book", 22)],                     # 2000 + 475 = 2475
    [("book", 15)] * 10,                             # ten books at 300 = 3000
    [("reference", 30), ("reference", 30), ("dvd", 30), ("book", 60)],  # 1500+1500+2000+800
    [("reference", 10), ("book", 1), ("dvd", 2)],    # 1500 + 0 + 0
    [("dvd", 0), ("book", -4)],                      # nothing owed
]
accounts = [[item(f"i{n}", kind, 100, late) for n, (kind, late) in enumerate(spec)] for spec in FIXED]
for _ in range(60):
    accounts.append([
        item(f"a{n}", rng.choice(TYPES), rng.randint(0, 500), rng.randint(-5, 40))
        for n in range(rng.randint(1, 8))
    ])

for items in accounts:
    expected_lines = {i["id"]: item_fine(i["type"], i["due_day"], i["returned_day"]) for i in items}
    expected_total = min(sum(expected_lines.values()), ACCOUNT_CAP)
    status, body = call({"items": items})
    try:
        got_lines = {line["id"]: line["fine_cents"] for line in body["items"]}
        got_total = body["total_cents"]
    except (TypeError, KeyError):
        got_lines, got_total = None, None
    if status != 0 or got_lines != expected_lines or got_total != expected_total:
        problems.append(
            f"{len(items)} items owing {sum(expected_lines.values())}: expected item fines {expected_lines} "
            f"and total {expected_total}, got {got_lines!r} and {got_total!r} (status {status})"
        )

finish(problems, f"account cap ok: {len(accounts)} accounts")
