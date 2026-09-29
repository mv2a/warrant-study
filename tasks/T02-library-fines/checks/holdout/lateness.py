"""H5: days_late is returned_day minus due_day, never below zero; on time or early owes nothing (C2)."""

import random

from _cmd import call, finish
from _model import TYPES

rng = random.Random(7331)
problems = []
pairs = [(0, 0), (1, 0), (20, 5), (10, 10), (10, 11), (999_999, 0), (0, 999_999), (365, 364), (7, 8)]
pairs += [(rng.randint(0, 300), rng.randint(0, 300)) for _ in range(80)]

checked = 0
for start in range(0, len(pairs), 5):
    batch = pairs[start:start + 5]
    items = [
        {"id": f"L{start + n}", "type": TYPES[(start + n) % 3], "due_day": due, "returned_day": back}
        for n, (due, back) in enumerate(batch)
    ]
    status, body = call({"items": items})
    try:
        got = {line["id"]: (line["days_late"], line["fine_cents"]) for line in body["items"]}
    except (TypeError, KeyError):
        got = None
    for request_item in items:
        due, back = request_item["due_day"], request_item["returned_day"]
        expected_late = max(0, back - due)
        line = got.get(request_item["id"]) if status == 0 and got else None
        checked += 1
        if line is None or line[0] != expected_late:
            problems.append(f"{request_item['type']} due {due}, returned {back}: expected days_late {expected_late}, got {line!r} (status {status})")
        elif back <= due and line[1] != 0:
            problems.append(f"{request_item['type']} due {due}, returned {back}: on time or early must owe 0, got {line[1]!r}")

finish(problems, f"days late ok: {checked} items")
