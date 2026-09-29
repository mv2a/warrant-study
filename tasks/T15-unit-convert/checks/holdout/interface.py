"""H8: the command's interface: fields, types, exit statuses and silent refusals (C5)."""

import json
import random

from _cmd import call, finish
from _units import KIND, UNITS, random_value

FIELDS = {"value", "unit", "dimension"}
rng = random.Random(1508)
problems = []

requests = []
for unit in UNITS:
    target = rng.choice([other for other in UNITS if KIND[other] == KIND[unit]])
    requests.append({"value": random_value(rng, 3, 2), "from": unit, "to": target, "places": rng.randint(0, 12)})
for request in requests:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{request}: expected one object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(isinstance(body[field], str) for field in FIELDS):
        problems.append(f"{request}: every field must be a string, got {body!r}")
    elif body["unit"] != request["to"]:
        problems.append(f"{request}: unit must be the 'to' unit {request['to']!r}, got {body['unit']!r}")
    elif body["dimension"] != KIND[request["to"]]:
        problems.append(f"{request}: dimension must be {KIND[request['to']]!r}, got {body['dimension']!r}")

padded = "\n  " + json.dumps({"value": "2", "from": "kg", "to": "g", "places": 0}) + "  \n\n"
status, body = call(raw=padded)
if status != 0 or body != {"value": "2000", "unit": "g", "dimension": "mass"}:
    problems.append(f"a request with whitespace around it: expected status 0 and 2000 g, got status {status} and {body!r}")

REFUSED = [
    ("an unknown unit", {"value": "1", "from": "furlong", "to": "m", "places": 0}),
    ("a value that is not a number", {"value": "one", "from": "m", "to": "cm", "places": 0}),
    ("a value given as a JSON number", {"value": 1, "from": "m", "to": "cm", "places": 0}),
    ("too many places", {"value": "1", "from": "m", "to": "cm", "places": 13}),
    ("a missing field", {"value": "1", "from": "m", "to": "cm"}),
    ("text that is not JSON", "one metre"),
]
for name, request in REFUSED:
    status, body = call(raw=request if isinstance(request, str) else json.dumps(request))
    if status != 2 or body is not None:
        problems.append(f"{name}: expected status 2 and nothing on standard output, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(requests) + 1} conversions, {len(REFUSED)} silent refusals")
