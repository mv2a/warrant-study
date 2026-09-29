"""H5: the command's interface: one JSON object in, one object of seven integers out, exit 0 or 2."""

import json
import random

from _cmd import call, finish
from _model import FIELDS, expected

rng = random.Random(4242)
problems = []


def valid(request, label, want=None):
    status, body = call(raw=request) if isinstance(request, str) else call(request)
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != set(FIELDS):
        problems.append(f"{label}: expected an object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[field]) is int for field in FIELDS):
        problems.append(f"{label}: every field must be a JSON integer, got {body!r}")
    elif want is not None and body != want:
        problems.append(f"{label}: expected {want}, got {body!r}")
    else:
        return body
    return None


for index in range(30):
    week = [rng.choice([0, rng.randint(1, 1440)]) for _ in range(7)]
    rate = rng.randint(1, 100000)
    body = valid({"minutes": week, "rate_cents": rate}, f"{week} at {rate}")
    if body is None:
        continue
    minutes = body["regular_minutes"] + body["overtime_minutes"] + body["double_minutes"]
    if minutes != sum(week):
        problems.append(f"{week}: the minute fields add up to {minutes}, not the {sum(week)} minutes worked")
    cents = body["regular_cents"] + body["overtime_cents"] + body["double_cents"]
    if body["total_cents"] != cents:
        problems.append(f"{week} at {rate}: total_cents {body['total_cents']} is not the sum {cents}")

week, rate = [600, 480, 0, 720, 30, 0, 0], 2150
want = expected(week, rate)
valid({"rate_cents": rate, "minutes": week}, "fields in the other order", want)
valid({"minutes": week, "rate_cents": rate, "employee": "E-17", "week": 39, "note": None},
      "extra fields, which must be ignored", want)
valid(json.dumps({"minutes": week, "rate_cents": rate}, indent=2) + "\n", "pretty-printed input", want)

for label, raw in [("text that is not JSON", "forty hours"),
                   ("a missing rate", '{"minutes": [480, 0, 0, 0, 0, 0, 0]}'),
                   ("a day over 1440 minutes", '{"minutes": [1441, 0, 0, 0, 0, 0, 0], "rate_cents": 1500}')]:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: a refusal must exit 2 and write nothing, got status {status} and {body!r}")

finish(problems, "interface ok: 33 valid and 3 refused requests")
