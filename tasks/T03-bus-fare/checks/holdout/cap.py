"""H4: a day's charges never pass the rider's cap: 1100 adult, 550 child, 440 senior."""

import random

from _cmd import call, finish

rng = random.Random(30304)
CAPS = {"adult": 1100, "child": 550, "senior": 440}
AGES = {"adult": (20, 60), "child": (6, 14), "senior": (66, 110)}  # clear of the age boundaries
# Upward trips only, and only zone spans whose concession fare is already a multiple of
# 5 cents, so this check depends on neither direction nor rounding.
SPANS = {"adult": [0, 1, 2, 3, 4, 5], "child": [0, 2, 4], "senior": [4]}
RATE = {"adult": 100, "child": 50, "senior": 40}


def trip(minute, start, end):
    return {"board_minute": minute, "from_zone": start, "to_zone": end}


def spaced(spans, first=60, gap=100):
    """Trips far enough apart that none is a transfer."""
    return [trip(first + gap * i, 1, 1 + span) for i, span in enumerate(spans)]


# (label, age, trips, expected fares)
CASES = [
    ("adult, two long trips", 30, spaced([5, 5]), [745, 355]),
    ("adult, three middling trips", 45, spaced([2, 2, 1]), [460, 460, 180]),
    ("adult, trips after the cap", 50, spaced([5, 3, 0, 0, 5]), [745, 355, 0, 0, 0]),
    ("adult, just under the cap", 20, spaced([0, 0, 0, 0]), [270, 270, 270, 270]),
    ("adult, 20 cents left", 20, spaced([0, 0, 0, 0, 0, 0]), [270, 270, 270, 270, 20, 0]),
    ("adult, transfers inside", 33, [trip(0, 1, 6), trip(30, 6, 1), trip(200, 1, 6), trip(250, 6, 1), trip(400, 1, 1)],
     [745, 0, 355, 0, 0]),
    ("child, two long trips", 10, spaced([4, 4]), [325, 225]),
    ("child, small trips", 7, spaced([0, 0, 0, 0, 0, 0]), [135, 135, 135, 135, 10, 0]),
    ("child, reaching the cap exactly", 13, spaced([2, 4, 0]), [230, 320, 0]),
    ("child, not the adult cap", 12, spaced([4, 4, 4, 4]), [325, 225, 0, 0]),
    ("senior, three long trips", 70, spaced([4, 4, 4]), [260, 180, 0]),
    ("senior, not the adult cap", 90, spaced([4, 4, 4, 4, 4]), [260, 180, 0, 0, 0]),
]


def model(kind, trips):
    fares, total, opened = [], 0, None
    for t in trips:
        if opened is not None and t["board_minute"] - opened <= 90:
            fare = 0
        else:
            opened = t["board_minute"]
            fare = (270 + 95 * (t["to_zone"] - t["from_zone"])) * RATE[kind] // 100
        fare = min(fare, CAPS[kind] - total)
        fares.append(fare)
        total += fare
    return fares


for number in range(60):
    kind = ("adult", "child", "senior")[number % 3]
    minute, trips = rng.randint(0, 200), []
    for _ in range(rng.randint(1, 10)):
        minute += rng.choice([91, 95, 130, 200])  # no transfers: those are H2's concern
        if minute > 1439:
            break
        start = rng.randint(1, 6 - max(SPANS[kind]))
        trips.append(trip(minute, start, start + rng.choice(SPANS[kind])))
    CASES.append((f"generated {kind} day {number + 1}", rng.randint(*AGES[kind]), trips, model(kind, trips)))

problems = []
for label, age, trips, fares in CASES:
    status, body = call({"age": age, "trips": trips})
    got = body.get("fares_cents") if isinstance(body, dict) else None
    total = body.get("total_cents") if isinstance(body, dict) else None
    kind = "child" if age <= 15 else "senior" if age >= 65 else "adult"
    if status != 0 or got != fares:
        problems.append(f"{label} (age {age}): expected {fares}, got {got!r} (status {status})")
    elif not isinstance(total, int) or total > CAPS[kind]:
        problems.append(f"{label} (age {age}): total {total!r} is over the {kind} cap of {CAPS[kind]}")

finish(problems, f"daily caps ok: {len(CASES)} days")
