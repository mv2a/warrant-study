"""P1: `convert` follows the interface in C5."""

from _cmd import call, finish

FIELDS = {"value", "unit", "dimension"}
problems = []

for request, dimension in (
    ({"value": "1", "from": "km", "to": "m", "places": 0}, "length"),
    ({"value": "3", "from": "gal", "to": "qt", "places": 1}, "volume"),
):
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(isinstance(body[field], str) for field in FIELDS):
        problems.append(f"{request}: every field must be a string, got {body!r}")
    elif body["unit"] != request["to"] or body["dimension"] != dimension:
        problems.append(f"{request}: expected unit {request['to']!r} and dimension {dimension!r}, got {body!r}")

status, body = call({"value": "1", "from": "furlong", "to": "m", "places": 0})
if status != 2 or body is not None:
    problems.append(f"an unknown unit must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "contract ok: 3 requests")
