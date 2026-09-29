"""H6: invalid requests are refused (status 2, nothing on standard output); valid edge cases are not."""

import json

from _cmd import call, finish

GOOD_TRIP = {"board_minute": 600, "from_zone": 2, "to_zone": 3}


def with_age(age):
    return json.dumps({"age": age, "trips": [GOOD_TRIP]})


def with_trip(**changes):
    trip = {**GOOD_TRIP, **changes}
    return json.dumps({"age": 30, "trips": [trip]})


def without(field):
    trip = {k: v for k, v in GOOD_TRIP.items() if k != field}
    return json.dumps({"age": 30, "trips": [trip]})


def ordered(*minutes):
    return json.dumps({"age": 30, "trips": [{**GOOD_TRIP, "board_minute": m} for m in minutes]})


INVALID = [
    ("text that isn't JSON", "thirty years old, zone 2 to zone 3"),
    ("an empty request", ""),
    ("a JSON list", json.dumps([30, [GOOD_TRIP]])),
    ("a JSON string", json.dumps("age 30")),
    ("a JSON number", "30"),
    ("JSON null", "null"),
    ("a truncated object", '{"age": 30, "trips": ['),
    ("a missing age", json.dumps({"trips": [GOOD_TRIP]})),
    ("a missing trips field", json.dumps({"age": 30})),
    ("an age of -1", with_age(-1)),
    ("an age of 121", with_age(121)),
    ("an age of 30.0", '{"age": 30.0, "trips": [{"board_minute": 600, "from_zone": 2, "to_zone": 3}]}'),
    ("an age of 30.5", with_age(30.5)),
    ('an age of "30"', with_age("30")),
    ("an age of true", with_age(True)),
    ("an age of false", with_age(False)),
    ("an age of null", with_age(None)),
    ("trips as an object", json.dumps({"age": 30, "trips": GOOD_TRIP})),
    ("trips as text", json.dumps({"age": 30, "trips": "none"})),
    ("trips as null", json.dumps({"age": 30, "trips": None})),
    ("a trip that is a number", json.dumps({"age": 30, "trips": [GOOD_TRIP, 5]})),
    ("a trip that is a list", json.dumps({"age": 30, "trips": [[600, 2, 3]]})),
    ("a trip without board_minute", without("board_minute")),
    ("a trip without from_zone", without("from_zone")),
    ("a trip without to_zone", without("to_zone")),
    ("a boarding minute of -1", with_trip(board_minute=-1)),
    ("a boarding minute of 1440", with_trip(board_minute=1440)),
    ("a boarding minute of 600.0", '{"age": 30, "trips": [{"board_minute": 600.0, "from_zone": 2, "to_zone": 3}]}'),
    ('a boarding minute of "600"', with_trip(board_minute="600")),
    ("a boarding minute of true", with_trip(board_minute=True)),
    ("a from_zone of 0", with_trip(from_zone=0)),
    ("a from_zone of 7", with_trip(from_zone=7)),
    ('a from_zone of "2"', with_trip(from_zone="2")),
    ("a from_zone of true", with_trip(from_zone=True)),
    ("a to_zone of 0", with_trip(to_zone=0)),
    ("a to_zone of 7", with_trip(to_zone=7)),
    ("a to_zone of 2.5", with_trip(to_zone=2.5)),
    ("a to_zone of null", with_trip(to_zone=None)),
    ("two trips out of order", ordered(600, 599)),
    ("a later trip out of order", ordered(100, 200, 300, 250)),
    ("out of order after a tie", ordered(500, 500, 499)),
    ("out of order and far apart", ordered(1439, 0)),
    ("a bad trip after good ones", json.dumps({"age": 30, "trips": [GOOD_TRIP, {**GOOD_TRIP, "to_zone": 9}]})),
]
VALID = [
    ("an age of 0", {"age": 0, "trips": [GOOD_TRIP]}),
    ("an age of 120", {"age": 120, "trips": [GOOD_TRIP]}),
    ("a boarding minute of 0", {"age": 30, "trips": [{**GOOD_TRIP, "board_minute": 0}]}),
    ("a boarding minute of 1439", {"age": 30, "trips": [{**GOOD_TRIP, "board_minute": 1439}]}),
    ("zones 1 and 6", {"age": 30, "trips": [{**GOOD_TRIP, "from_zone": 1, "to_zone": 6}]}),
    ("zones 6 and 1", {"age": 30, "trips": [{**GOOD_TRIP, "from_zone": 6, "to_zone": 1}]}),
    ("trips boarding in the same minute", {"age": 30, "trips": [GOOD_TRIP, GOOD_TRIP, GOOD_TRIP]}),
    ("an empty trips list", {"age": 30, "trips": []}),
]

problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: expected a refusal (status 2, no output), got status {status} and {body!r}")
for name, request in VALID:
    status, body = call(request)
    fares = body.get("fares_cents") if isinstance(body, dict) else None
    if status != 0 or not isinstance(fares, list) or len(fares) != len(request["trips"]):
        problems.append(f"{name}: expected to be priced (status 0), got status {status} and {body!r}")
status, body = call({"age": 30, "trips": []})
if status == 0 and body != {"fares_cents": [], "total_cents": 0}:
    problems.append(f"an empty trips list should cost nothing, got {body!r}")

finish(problems, f"validation ok: {len(INVALID)} refused, {len(VALID)} accepted")
