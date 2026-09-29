"""X8 (C5): the convert command's interface: one JSON object in, exactly three string fields out,
exit status 0 on success, exit status 2 and nothing at all on standard output on refusal."""

import json

from _audit import DIMENSION, KINDS, expected, finish, raw_run_all, short

FIELDS = {"value", "unit", "dimension"}
problems = []

# One success for every unit as the target, read from the raw standard output: (stdin text, request).
successes = []
for table in KINDS.values():
    units = list(table)
    for i, target in enumerate(units):
        req = {"value": "2", "from": units[(i + 3) % len(units)], "to": target, "places": 3}
        successes.append((json.dumps(req), req))

# The same request written in other valid JSON forms must be read the same way.
SAME = {"value": "3", "from": "in", "to": "cm", "places": 1}
forms = [
    '{"places": 1, "to": "cm", "from": "in", "value": "3"}',
    '{\n  "value": "3",\n  "from": "in",\n  "to": "cm",\n  "places": 1\n}\n',
    '\n\t {"value":"3","from":"in","to":"cm","places":1}',
    '{"value": "3", "from": "in", "to": "cm", "places": 1}\n\n',
    '{"\\u0076alue": "\\u0033", "from": "\\u0069n", "to": "cm", "places": 1}',
]
successes += [(text, SAME) for text in forms]

results = raw_run_all([text for text, _ in successes])
for (text, req), (status, out) in zip(successes, results):
    target = req["to"]
    label = short(text, 70)
    if status != 0:
        problems.append(f"{label}: exited with status {status}, expected 0")
        continue
    try:
        body = json.loads(out)
    except (TypeError, ValueError):
        problems.append(f"{label}: standard output is not one JSON object: {short(out, 60)}")
        continue
    if not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{label}: expected an object with exactly {sorted(FIELDS)}, got {short(body, 60)}")
    elif not all(isinstance(body[f], str) for f in FIELDS):
        problems.append(f"{label}: every output field must be a string, got {short(body, 60)}")
    elif body["unit"] != target or body["dimension"] != DIMENSION[target]:
        problems.append(f"{label}: expected unit {target!r} and dimension {DIMENSION[target]!r}, got {short(body, 60)}")
    elif body["value"] != expected(req["value"], req["from"], req["to"], req["places"]):
        problems.append(f"{label}: expected value {expected(req['value'], req['from'], req['to'], req['places'])!r}, got {body['value']!r}")

# Refusals: exit status exactly 2 and not a single character on standard output.
REFUSALS = [
    '{"value": "1", "from": "furlongs", "to": "m", "places": 0}',
    '{"value": "1", "from": "m", "to": "kg", "places": 0}',
    '{"value": "1", "from": "gal", "to": "lb", "places": 0}',
    '{"value": "5.", "from": "m", "to": "cm", "places": 0}',
    '{"value": "1", "from": "m", "to": "cm", "places": 13}',
    '{"value": "1", "from": "m", "to": "cm", "places": 0, "why": "extra"}',
    '{"value": "1", "from": "m", "to": "cm"}',
    'not json at all',
    '',
    '[1, 2, 3]',
]
for text, (status, out) in zip(REFUSALS, raw_run_all(REFUSALS)):
    if status != 2 or out != "":
        problems.append(f"{short(text, 60)}: must exit 2 and write nothing, got status {status} and output {short(out, 40)}")

finish(problems, f"interface ok: {len(successes) - len(forms)} units as targets, {len(forms)} input forms, {len(REFUSALS)} clean refusals")
