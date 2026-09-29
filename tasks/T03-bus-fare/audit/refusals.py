"""X6 (C2): every kind of invalid request is refused with status 2 and nothing on standard output."""

import json
import random

from _audit import call_many_raw, short, trip
from _cmd import finish

GOOD_TRIP = trip(615, 2, 4)
DROP = object()


def req(age=47, trips=DROP, **extra):
    body = {"age": age, "trips": [GOOD_TRIP] if trips is DROP else trips}
    body.update(extra)
    return body


def with_trip(**changes):
    t = dict(GOOD_TRIP)
    for key, value in changes.items():
        if value is DROP:
            del t[key]
        else:
            t[key] = value
    return t


NOT_INTEGERS = [12.0, 12.5, "12", True, False, None, [12], {"n": 12}]

texts = [
    # Text that isn't a JSON object.
    "", "   \n", "bus", "{", '{"age": 47, "trips": []', "{'age': 47, 'trips': []}",
    "[]", '[{"age": 47, "trips": []}]', "47", '"age"', "null", "true",
    '{"age": 47, "trips": []} {"age": 47, "trips": []}', '{"age": 47, "trips": []} x',
    '{"age": NaN, "trips": []}', '{"age": 47, "trips": [], }',
    # Numbers written with a fraction or exponent are not JSON integers.
    '{"age": 4.7e1, "trips": []}', '{"age": 3e1, "trips": []}',
    '{"age": 47, "trips": [{"board_minute": 6e2, "from_zone": 1, "to_zone": 2}]}',
    '{"age": 47, "trips": [{"board_minute": 600, "from_zone": 1.0, "to_zone": 2}]}',
]

requests = [
    # Missing fields.
    {}, {"trips": []}, {"age": 47}, {"Age": 47, "trips": []}, {"age": 47, "Trips": []},
    # Age out of range.
    req(age=-1), req(age=121), req(age=-47), req(age=1000), req(age=10 ** 20), req(age=121, trips=[]),
    # Trips that isn't a list.
    req(trips={}), req(trips="[]"), req(trips=5), req(trips=None), req(trips=True), req(trips=GOOD_TRIP),
    # A trip that isn't an object.
    req(trips=[5]), req(trips=["bus"]), req(trips=[None]), req(trips=[[615, 2, 4]]), req(trips=[True]),
    req(trips=[GOOD_TRIP, 7]), req(trips=[GOOD_TRIP, []]),
    # A trip lacking a field.
    req(trips=[{}]),
    req(trips=[with_trip(board_minute=DROP)]), req(trips=[with_trip(from_zone=DROP)]), req(trips=[with_trip(to_zone=DROP)]),
    req(trips=[GOOD_TRIP, trip(700, 4, 4), {"board_minute": 800, "from_zone": 4}]),
    req(trips=[{"minute": 615, "from_zone": 2, "to_zone": 4}]),
    # Boarding minute out of range.
    req(trips=[with_trip(board_minute=-1)]), req(trips=[with_trip(board_minute=1440)]),
    req(trips=[with_trip(board_minute=-600)]), req(trips=[with_trip(board_minute=99999)]),
    req(trips=[trip(1439, 1, 1), trip(1440, 1, 1)]),
    # Zones out of range, on either end.
    req(trips=[with_trip(from_zone=0)]), req(trips=[with_trip(from_zone=7)]), req(trips=[with_trip(from_zone=-2)]),
    req(trips=[with_trip(to_zone=0)]), req(trips=[with_trip(to_zone=7)]), req(trips=[with_trip(to_zone=60)]),
    req(trips=[GOOD_TRIP, trip(900, 6, 7)]),
    # Trips out of boarding order.
    req(trips=[trip(600, 1, 2), trip(599, 2, 3)]),
    req(trips=[trip(0, 1, 2), trip(100, 2, 3), trip(50, 3, 4)]),
    req(trips=[trip(100, 1, 1), trip(100, 1, 1), trip(99, 1, 1)]),
    req(trips=[trip(1439, 5, 5), trip(0, 5, 5)]),
    req(trips=[trip(200, 1, 1), trip(300, 1, 1), trip(400, 1, 1), trip(250, 1, 1)]),
    # Refusal does not depend on the price: a free rider, a capped day and a transfer are still checked.
    req(age=3, trips=[with_trip(to_zone=7)]), req(age=2, trips=[trip(10, 1, 1), trip(5, 1, 1)]),
    req(age=0, trips=[with_trip(board_minute="615")]),
    req(age=30, trips=[trip(0, 1, 6), trip(100, 6, 1), trip(200, 1, 6), trip(300, 6, 0)]),
    req(age=30, trips=[trip(0, 1, 6), trip(100, 6, 1), trip(200, 1, 6), trip(150, 6, 1)]),
    req(age=30, trips=[trip(500, 1, 2), trip(520, 2, True)]),
    # An empty trips list does not excuse a bad age.
    req(age=12.0, trips=[]), req(age=None, trips=[]), req(age="12", trips=[]),
]

# Every numeric field written as anything other than a JSON integer.
for value in NOT_INTEGERS:
    requests.append(req(age=value))
    for key in ("board_minute", "from_zone", "to_zone"):
        requests.append(req(trips=[with_trip(**{key: value})]))

# Seeded mutations: take a valid day and break exactly one thing in one trip.
rng = random.Random(604113)
BREAKS = [
    ("board_minute", [-1, 1440, 2000, 600.0, "600", True, None]),
    ("from_zone", [0, 7, 3.0, "3", True, False, None]),
    ("to_zone", [0, 7, 9, 5.0, "5", True, None]),
]
for _ in range(40):
    minute, trips = rng.randint(0, 300), []
    for _ in range(rng.randint(1, 7)):
        trips.append(trip(minute, rng.randint(1, 6), rng.randint(1, 6)))
        minute = min(1439, minute + rng.choice([0, 20, 90, 91, 200]))
    victim = rng.randrange(len(trips))
    key, values = rng.choice(BREAKS)
    trips[victim] = dict(trips[victim], **{key: rng.choice(values)})
    requests.append(req(age=rng.choice([1, 8, 16, 40, 70, 120]), trips=trips))

all_texts = texts + [json.dumps(r) for r in requests]
problems = []
for text, (status, body) in zip(all_texts, call_many_raw(all_texts)):
    if status != 2 or body is not None:
        problems.append(f"{short(text)}: expected status 2 and no output, got status {status} and {short(body, 80)}")

finish(problems, f"refusals ok: {len(all_texts)} invalid requests")
