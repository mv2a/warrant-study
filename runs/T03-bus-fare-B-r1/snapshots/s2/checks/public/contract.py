"""P1: `fare` follows the interface in C3."""

from _cmd import call, finish

FIELDS = {"fares_cents", "total_cents"}
REQUESTS = [
    {"age": 30, "trips": [{"board_minute": 600, "from_zone": 1, "to_zone": 2}]},
    {"age": 8, "trips": [{"board_minute": 420, "from_zone": 2, "to_zone": 2}, {"board_minute": 900, "from_zone": 2, "to_zone": 4}]},
    {"age": 70, "trips": []},
]
problems = []

for request in REQUESTS:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not isinstance(body["fares_cents"], list) or len(body["fares_cents"]) != len(request["trips"]):
        problems.append(f"{request}: fares_cents must list one fare per trip, got {body['fares_cents']!r}")
    elif not all(type(fare) is int for fare in body["fares_cents"]) or type(body["total_cents"]) is not int:
        problems.append(f"{request}: every amount must be a whole number of cents, got {body!r}")
    elif body["total_cents"] != sum(body["fares_cents"]):
        problems.append(f"{request}: total_cents must be the sum of fares_cents, got {body!r}")

refused = {"age": 30, "trips": [{"board_minute": 600, "from_zone": 1, "to_zone": 7}]}
status, body = call(refused)
if status != 2 or body is not None:
    problems.append(f"a zone of 7 must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "contract ok: 4 requests")
