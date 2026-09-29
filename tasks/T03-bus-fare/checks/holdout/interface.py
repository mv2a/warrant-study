"""H7: `fare` reads one JSON object and writes exactly {fares_cents, total_cents}, or refuses with status 2 and no output."""

import json
import random

from _cmd import call, finish

rng = random.Random(30307)
FIELDS = {"fares_cents", "total_cents"}


def trip(minute, start, end):
    return {"board_minute": minute, "from_zone": start, "to_zone": end}


def random_request():
    minute, trips = rng.randint(0, 300), []
    for _ in range(rng.randint(0, 8)):
        minute += rng.choice([0, 15, 60, 90, 91, 150])
        if minute > 1439:
            break
        trips.append(trip(minute, rng.randint(1, 6), rng.randint(1, 6)))
    return {"age": rng.randint(0, 120), "trips": trips}


def shape_problem(request, status, body):
    if status != 0:
        return f"exited with status {status}, expected 0"
    if not isinstance(body, dict) or set(body) != FIELDS:
        return f"expected one object with exactly {sorted(FIELDS)}, got {body!r}"
    fares, total = body["fares_cents"], body["total_cents"]
    if not isinstance(fares, list) or len(fares) != len(request["trips"]):
        return f"fares_cents must hold one fare per trip, got {fares!r}"
    if not all(type(f) is int for f in fares) or type(total) is not int:
        return f"every amount must be a whole number of cents, got {body!r}"
    if total != sum(fares):
        return f"total_cents must be the sum of fares_cents, got {body!r}"
    return None


problems = []
requests = [random_request() for _ in range(40)]
for request in requests:
    status, body = call(request)
    problem = shape_problem(request, status, body)
    if problem:
        problems.append(f"age {request['age']}, {len(request['trips'])} trips: {problem}")
        continue
    # The same request, pretty-printed across lines, is the same request.
    status2, body2 = call(raw=json.dumps(request, indent=2) + "\n")
    if (status2, body2) != (status, body):
        problems.append(f"age {request['age']}: pretty-printed JSON gave {body2!r} (status {status2}), not {body!r}")
    # Fields the interface does not name are ignored, in the request and in each trip.
    noisy = {"card": "A-17", **request, "note": {"x": 1}, "trips": [{**t, "route": "44", "stop": 12} for t in request["trips"]]}
    status3, body3 = call(noisy)
    if (status3, body3) != (status, body):
        problems.append(f"age {request['age']}: extra fields changed the answer to {body3!r} (status {status3}), not {body!r}")

# Fares come back in the order the trips were given.
request = {"age": 30, "trips": [trip(60, 1, 3), trip(200, 4, 4), trip(400, 2, 3)]}
status, body = call(request)
if status != 0 or not isinstance(body, dict) or body.get("fares_cents") != [460, 270, 365]:
    problems.append(f"fares must be listed in trip order: expected [460, 270, 365], got {body!r} (status {status})")

# Refusals: status 2 and nothing on standard output.
for raw in ("not json", "[]", '{"age": 30}', '{"age": 30, "trips": [{"board_minute": 5, "from_zone": 0, "to_zone": 1}]}'):
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{raw!r}: a refusal must exit 2 with nothing on standard output, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(requests) * 3 + 5} requests")
