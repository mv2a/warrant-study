"""H5: child and senior fares are rounded down to a multiple of 5 cents."""

import random

from _cmd import call, finish

rng = random.Random(30305)
# adult fare by boundaries crossed, and the concession fares the intent implies
ADULT = {span: 270 + 95 * span for span in range(6)}
CHILD = {0: 135, 1: 180, 2: 230, 3: 275, 4: 325, 5: 370}  # halves of 365, 555 and 745 end in .5
SENIOR = {0: 105, 1: 145, 2: 180, 3: 220, 4: 260, 5: 295}  # 40%: 108, 146, 184, 222, 260, 298


def trip(minute, start, end):
    return {"board_minute": minute, "from_zone": start, "to_zone": end}


problems = []
count = 0
for kind, table, ages in (("child", CHILD, (6, 14)), ("senior", SENIOR, (66, 110))):  # clear of the age boundaries
    for span, expected in table.items():
        for _ in range(4):
            age = rng.randint(*ages)
            start = rng.randint(1, 6 - span)  # upward, so direction plays no part
            status, body = call({"age": age, "trips": [trip(rng.randint(0, 1439), start, start + span)]})
            fares = body.get("fares_cents") if isinstance(body, dict) else None
            count += 1
            if status != 0 or not isinstance(fares, list) or len(fares) != 1:
                problems.append(f"{kind} aged {age}, {ADULT[span]}-cent adult trip: expected [{expected}], got {fares!r} (status {status})")
            elif type(fares[0]) is not int or fares[0] != expected:
                problems.append(f"{kind} aged {age}, {ADULT[span]}-cent adult trip: expected {expected} cents, got {fares[0]!r}")

finish(problems, f"rounding ok: {count} concession trips")
