"""X1 (G1): adult fares are 270 cents plus 95 cents per zone boundary, in either direction."""

from _audit import ADULT_TABLE, adult_fare, check_cases, trip
from _cmd import finish

ADULT_AGES = [16, 23, 38, 51, 64]
MINUTES = [0, 1439, 377, 812, 1063, 45]

cases = []
n = 0
for start in range(1, 7):
    for end in range(1, 7):
        age = ADULT_AGES[n % len(ADULT_AGES)]
        minute = MINUTES[n % len(MINUTES)]
        n += 1
        expected = ADULT_TABLE[abs(start - end)]
        assert expected == adult_fare(start, end)
        cases.append((f"age {age}, zone {start} to {end} at minute {minute}", {"age": age, "trips": [trip(minute, start, end)]}, [expected]))

# Several paid trips in one day (each more than 90 minutes apart, staying under the cap):
# every one is priced on its own boundaries.
cases += [
    ("age 52, three separate trips", {"age": 52, "trips": [trip(100, 1, 1), trip(300, 3, 2), trip(500, 2, 4)]}, [270, 365, 460]),
    ("age 29, two separate trips", {"age": 29, "trips": [trip(610, 6, 1), trip(702, 4, 4)]}, [745, 270]),
    ("age 64, two separate trips", {"age": 64, "trips": [trip(5, 5, 2), trip(1400, 2, 4)]}, [555, 460]),
    ("age 17, two separate trips", {"age": 17, "trips": [trip(233, 3, 6), trip(1000, 6, 4)]}, [555, 460]),
]

finish(check_cases(cases), f"adult fares ok: {len(cases)} requests, all 36 zone pairs")
