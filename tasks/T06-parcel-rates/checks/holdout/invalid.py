"""H7 (C3): invalid requests are refused, never priced."""

import json

from _cmd import call, finish
from _model import refused

GOOD = {"zone": 2, "weight_g": 1200, "length_cm": 30, "width_cm": 20, "height_cm": 10}


def variant(field, value):
    return json.dumps({**GOOD, field: value})


def without(field):
    return json.dumps({k: v for k, v in GOOD.items() if k != field})


INVALID = [
    ("text that isn't JSON", "a parcel to zone 2"),
    ("an empty request", ""),
    ("JSON with bare keys", "{zone: 2, weight_g: 1200}"),
    ("a JSON object cut short", '{"zone": 2, "weight_g": 1200,'),
    ("a list", "[2, 1200, 30, 20, 10]"),
    ("a string", '"zone 2, 1200 g"'),
    ("a number", "1200"),
    ("null", "null"),
    ("true", "true"),
    ("a weight of NaN", '{"zone": 2, "weight_g": NaN, "length_cm": 30, "width_cm": 20, "height_cm": 10}'),
]
INVALID += [(f"no {field}", without(field)) for field in GOOD]
INVALID += [(f"zone {value!r}", variant("zone", value)) for value in (0, 5, -1, 12, "2", True, 2.5, None, [2])]
INVALID += [(f"weight_g {value!r}", variant("weight_g", value)) for value in (0, -5, 1200.5, "1200", True, False, None)]
INVALID += [
    (f"{field} {value!r}", variant(field, value))
    for field in ("length_cm", "width_cm", "height_cm")
    for value in (0, -10, 10.5, "10", True, None)
]
# C3: a whole value written with a decimal point or an exponent is not a JSON integer.
INVALID += [(f"{field} {float(value)!r}", variant(field, float(value))) for field, value in GOOD.items()]
INVALID += [("weight_g 1.2e3", '{"zone": 2, "weight_g": 1.2e3, "length_cm": 30, "width_cm": 20, "height_cm": 10}')]
problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if not refused(status, body):
        problems.append(f"{name}: expected a refusal with status 2, got status {status} and {body!r}")

status, body = call(GOOD)
if status != 0:
    problems.append(f"the valid request these are built from was not priced: status {status}, {body!r}")

finish(problems, f"invalid requests ok: {len(INVALID)} refused")
