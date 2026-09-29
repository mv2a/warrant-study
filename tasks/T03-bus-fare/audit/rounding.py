"""X5 (C1): whole cents; child and senior fares rounded down to a multiple of 5 cents."""

from _audit import CHILD_TABLE, SENIOR_TABLE, call_many, check_cases, shape_problem, trip
from _cmd import finish

# Exact rounded fares for every distance, both directions, at several ages in each band.
# Unrounded: child 135, 182.5, 230, 277.5, 325, 372.5; senior 108, 146, 184, 222, 260, 298.
cases = []
for age, table, kind in [(5, CHILD_TABLE, "child"), (10, CHILD_TABLE, "child"), (15, CHILD_TABLE, "child"),
                         (65, SENIOR_TABLE, "senior"), (83, SENIOR_TABLE, "senior"), (120, SENIOR_TABLE, "senior")]:
    for crossed in range(6):
        for start, end in [(1, 1 + crossed), (6, 6 - crossed)]:
            if crossed == 0 and start == 6:
                start = end = 4
            minute = (age * 11 + crossed * 97 + start) % 1440
            cases.append((f"{kind} age {age}, zone {start} to {end}", {"age": age, "trips": [trip(minute, start, end)]}, [table[crossed]]))

# The example in C1: half of 365 cents is charged as 180, even as the second paid trip of a day.
cases.append(("C1 example in a day", {"age": 14, "trips": [trip(300, 2, 2), trip(400, 3, 4)]}, [135, 180]))
# Rounding happens per trip, not on the day's total: 3 x 182.5 would be 547.5, but it is 3 x 180.
cases.append(("per-trip rounding, child", {"age": 7, "trips": [trip(100, 1, 2), trip(200, 2, 3), trip(300, 3, 2)]}, [180, 180, 180]))
# Senior: 146 + 146 would be 292 -> 290 if rounded on the total; per trip it is 145 + 145.
cases.append(("per-trip rounding, senior", {"age": 68, "trips": [trip(100, 5, 6), trip(200, 6, 5)]}, [145, 145]))

problems = check_cases(cases)

# Every amount in a busy day is a whole number of cents and a multiple of 5.
busy = [{"age": age, "trips": [trip(60 * k, 1 + k % 6, 6 - (k * 5) % 6) for k in range(24)]} for age in (6, 13, 66, 95, 40)]
for request, (status, body) in zip(busy, call_many(busy)):
    wrong = shape_problem(request, status, body)
    if wrong:
        problems.append(f"busy day age {request['age']}: {wrong}")
    elif any(f % 5 for f in body["fares_cents"]) or any(f < 0 for f in body["fares_cents"]):
        problems.append(f"busy day age {request['age']}: amounts must be non-negative multiples of 5 cents, got {body['fares_cents']}")

finish(problems, f"rounding ok: {len(cases) + len(busy)} requests")
