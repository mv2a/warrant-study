"""X8 (C3): the fare command's interface: request and reply shape, exit statuses, ignored fields."""

import json

from _audit import call_many, call_many_raw, expected_body, shape_problem, short, trip
from _cmd import finish

problems = []

# 1. Replies have exactly fares_cents and total_cents, one integer per trip in the order
#    given, total equal to their sum, exit status 0. Checked on days of 0 to 14 trips.
plain = [
    {"age": 34, "trips": []},
    {"age": 34, "trips": [trip(480, 3, 1)]},
    {"age": 34, "trips": [trip(100, 1, 1), trip(200, 1, 2), trip(300, 1, 3)]},  # distinct fares, order visible
    {"age": 34, "trips": [trip(300, 1, 3), trip(400, 1, 2), trip(500, 1, 1)]},
    {"age": 11, "trips": [trip(60 * k + 7, 1 + k % 6, 1 + (k * 7) % 6) for k in range(14)]},
    {"age": 67, "trips": [trip(1000, 4, 6), trip(1100, 6, 4)]},
    {"age": 1, "trips": [trip(5, 2, 2)]},
]
for request, (status, body) in zip(plain, call_many(plain)):
    wrong = shape_problem(request, status, body)
    if wrong:
        problems.append(f"{short(request, 90)}: {wrong}")
    elif body != expected_body(request["age"], request["trips"]):
        problems.append(f"{short(request, 90)}: expected {expected_body(request['age'], request['trips'])}, got {body}")

# 2. Fields not named in the interface are ignored, in the request and in each trip,
#    even when they look like invalid values of the named fields.
base = {"age": 43, "trips": [trip(420, 1, 4), trip(470, 4, 6), trip(700, 6, 6)]}
noisy = {
    "rider": "R-17", "age_band": "senior", "zone": 7, "currency": "EUR", "total_cents": 1, "ages": [3],
    "age": 43, "extra": 30.5, "discount": None, "day": "2031-02-03",
    "trips": [
        dict(trip(420, 1, 4), line="12A", fare_cents=9999, board_minute_text="07:00", note=None),
        dict(trip(470, 4, 6), vehicle={"id": 3}, to_zone_name="Harbour", minute=-5, zone=0),
        dict(trip(700, 6, 6), transfer=False, paid=True, age=4),
    ],
}
reordered = {"trips": [{"to_zone": t["to_zone"], "board_minute": t["board_minute"], "from_zone": t["from_zone"]} for t in base["trips"]], "age": 43}
variants = [base, noisy, reordered]
replies = call_many(variants)
wanted = expected_body(43, base["trips"])
for name, request, (status, body) in zip(["plain", "with unknown fields", "keys reordered"], variants, replies):
    wrong = shape_problem(request, status, body)
    if wrong:
        problems.append(f"request {name}: {wrong}")
    elif body != wanted:
        problems.append(f"request {name}: expected {wanted}, got {body}")

# 3. One JSON object on standard input, however it is laid out.
layouts = [
    json.dumps(base) + "\n",
    "\n  " + json.dumps(base) + "  \n\n",
    json.dumps(base, indent=4),
    json.dumps(base, separators=(",", ":")),
]
for text, (status, body) in zip(layouts, call_many_raw(layouts)):
    if status != 0 or body != wanted:
        problems.append(f"layout {text[:30]!r}...: expected {wanted} with status 0, got {body!r} (status {status})")

# 4. A refused request exits with status 2 and writes nothing on standard output.
refused = ["{not json", json.dumps({"age": 43}), json.dumps({"age": 43, "trips": [trip(10, 0, 3)]}),
           json.dumps({"age": 43, "trips": [trip(10, 1, 2), trip(9, 2, 3)]})]
for text, (status, body) in zip(refused, call_many_raw(refused)):
    if status != 2:
        problems.append(f"{text}: a refusal must exit with status 2, got {status}")
    if body is not None:
        problems.append(f"{text}: a refusal must write nothing on standard output, got {short(body, 80)}")

# 5. The same request gives the same reply every time.
again = call_many([base] * 4)
if len({json.dumps(body, sort_keys=True) for _, body in again}) != 1:
    problems.append(f"the same request gave different replies: {[body for _, body in again]}")

finish(problems, f"interface ok: {len(plain) + len(variants) + len(layouts) + len(refused) + len(again)} requests")
