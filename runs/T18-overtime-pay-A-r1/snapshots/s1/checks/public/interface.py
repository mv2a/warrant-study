"""P1: `pay` follows the interface in the intent (C2), and refuses a few invalid requests (C3)."""

from _cmd import call, finish

FIELDS = {"regular_minutes", "overtime_minutes", "double_minutes",
          "regular_cents", "overtime_cents", "double_cents", "total_cents"}
problems = []

for request in ({"minutes": [480, 480, 0, 0, 0, 0, 0], "rate_cents": 1500},
                {"minutes": [0, 0, 0, 0, 0, 0, 0], "rate_cents": 1}):
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[field]) is int for field in FIELDS):
        problems.append(f"{request}: every field must be an integer, got {body!r}")
    elif body["regular_minutes"] + body["overtime_minutes"] + body["double_minutes"] != sum(request["minutes"]):
        problems.append(f"{request}: the minute fields must add up to {sum(request['minutes'])}, got {body!r}")

REFUSED = [
    ("a list of six days", {"minutes": [480, 480, 480, 480, 480, 480], "rate_cents": 1500}),
    ("a negative day", {"minutes": [480, -30, 0, 0, 0, 0, 0], "rate_cents": 1500}),
    ("a rate of zero", {"minutes": [480, 0, 0, 0, 0, 0, 0], "rate_cents": 0}),
]
for name, request in REFUSED:
    status, body = call(request)
    if status != 2 or body is not None:
        problems.append(f"{name} must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "interface ok: 2 valid and 3 refused requests")
