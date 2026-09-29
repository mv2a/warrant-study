"""H1: an adult fare is 270 cents plus 95 cents per zone boundary crossed, in either direction."""

import random

from _cmd import call, finish

rng = random.Random(30301)


def trip(minute, start, end):
    return {"board_minute": minute, "from_zone": start, "to_zone": end}


problems = []
count = 0

# Every ordered pair of zones, one trip each, for adults of middling age.
pairs = [(a, b) for a in range(1, 7) for b in range(1, 7)]
pairs += [(rng.randint(1, 6), rng.randint(1, 6)) for _ in range(24)]
for start, end in pairs:
    age, minute = rng.randint(20, 60), rng.randint(0, 1439)
    expected = 270 + 95 * abs(start - end)
    status, body = call({"age": age, "trips": [trip(minute, start, end)]})
    fares = body.get("fares_cents") if isinstance(body, dict) else None
    count += 1
    if status != 0 or fares != [expected]:
        problems.append(f"age {age}, zone {start} to {end}: expected [{expected}], got {fares!r} (status {status})")

# Out and back on the same day, far enough apart that neither trip is a transfer
# and the total stays under the adult cap.
for start in range(1, 7):
    for end in range(1, 7):
        if not 1 <= abs(start - end) <= 2:
            continue
        age, minute = rng.randint(20, 60), rng.randint(0, 1200)
        back = minute + rng.randint(91, 239)
        one_way = 270 + 95 * abs(start - end)
        status, body = call({"age": age, "trips": [trip(minute, start, end), trip(back, end, start)]})
        fares = body.get("fares_cents") if isinstance(body, dict) else None
        count += 1
        if status != 0 or fares != [one_way, one_way]:
            problems.append(f"age {age}, zone {start} to {end} and back: expected [{one_way}, {one_way}], got {fares!r} (status {status})")

finish(problems, f"zone fares ok: {count} adult days")
