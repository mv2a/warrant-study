"""H3: age sets the fare: under 5 free, 5-15 half, 16-64 full, 65 and over 40%."""

from _cmd import call, finish


def trip(minute, start, end):
    return {"board_minute": minute, "from_zone": start, "to_zone": end}


def expected(age, adult):
    if age < 5:
        return 0
    if age <= 15:
        return adult // 2
    if age >= 65:
        return adult * 40 // 100
    return adult


problems = []
count = 0
# Every age from 0 to 120 on a trip crossing four boundaries (650 cents for an adult),
# where both concessions come out at a whole multiple of 5 cents.
for age in range(0, 121):
    start = 1 + age % 2
    status, body = call({"age": age, "trips": [trip(480 + age, start, start + 4)]})
    fares = body.get("fares_cents") if isinstance(body, dict) else None
    count += 1
    if status != 0 or fares != [expected(age, 650)]:
        problems.append(f"age {age}, 650-cent adult trip: expected [{expected(age, 650)}], got {fares!r} (status {status})")

# Near each boundary, trips within one zone (270) and across two boundaries (460),
# which halve exactly for children.
for age in (0, 1, 4, 5, 6, 14, 15, 16, 17, 63, 64):
    for start, end, adult in ((2, 2, 270), (3, 5, 460)):
        status, body = call({"age": age, "trips": [trip(700, start, end)]})
        fares = body.get("fares_cents") if isinstance(body, dict) else None
        count += 1
        if status != 0 or fares != [expected(age, adult)]:
            problems.append(f"age {age}, {adult}-cent adult trip: expected [{expected(age, adult)}], got {fares!r} (status {status})")

# Riders under 5 ride free however far and however often they travel.
for age in (0, 2, 4):
    trips = [trip(minute, 1, 6) for minute in (60, 200, 400, 600, 800)]
    status, body = call({"age": age, "trips": trips})
    count += 1
    if status != 0 or not isinstance(body, dict) or body.get("fares_cents") != [0] * 5 or body.get("total_cents") != 0:
        problems.append(f"age {age}, five long trips: expected all free, got {body!r} (status {status})")

finish(problems, f"fare classes ok: {count} requests")
