"""H9: 150 generated days, every fare compared with the rules of G1-G4 and C1 together."""

import random

from _cmd import call, finish

rng = random.Random(30309)
AGES = [0, 4, 5, 6, 10, 15, 16, 17, 30, 45, 63, 64, 65, 66, 80, 120]


def expected(age, trips):
    if age < 5:
        percent, cap = 0, 0
    elif age < 16:
        percent, cap = 50, 550
    elif age < 65:
        percent, cap = 100, 1100
    else:
        percent, cap = 40, 440
    fares, total, opened = [], 0, None
    for t in trips:
        if opened is not None and t["board_minute"] - opened <= 90:
            fare = 0
        else:
            opened = t["board_minute"]
            adult = 270 + 95 * abs(t["to_zone"] - t["from_zone"])
            fare = adult * percent // 100 // 5 * 5
        fare = min(fare, cap - total)
        fares.append(fare)
        total += fare
    return {"fares_cents": fares, "total_cents": total}


problems = []
days = 150
for number in range(days):
    age = rng.choice(AGES) if number % 2 else rng.randint(0, 120)
    minute, trips = rng.randint(0, 500), []
    for _ in range(rng.randint(0, 9)):
        minute += rng.choice([0, 1, 30, 89, 90, 91, 100, 180])
        if minute > 1439:
            break
        trips.append({"board_minute": minute, "from_zone": rng.randint(1, 6), "to_zone": rng.randint(1, 6)})
    want = expected(age, trips)
    status, body = call({"age": age, "trips": trips})
    if status != 0 or body != want:
        problems.append(f"day {number + 1} (age {age}, {len(trips)} trips): expected {want}, got {body!r} (status {status})")

finish(problems, f"whole days ok: {days} generated days")
