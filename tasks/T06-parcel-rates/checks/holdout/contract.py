"""H5 (C1): the command's interface: request and response fields, exit statuses, and silent refusals."""

import random

from _cmd import call, finish
from _model import FIELDS, parcel, random_parcel

rng = random.Random(6050)
problems = []

requests = [random_parcel(rng) for _ in range(40)]
for p in requests:
    status, body = call(p)
    if status != 0:
        problems.append(f"{p}: exited with status {status}, expected 0")
    elif not isinstance(body, dict) or set(body) != FIELDS:
        problems.append(f"{p}: expected one object with exactly {sorted(FIELDS)}, got {body!r}")
    elif not all(type(body[field]) is int for field in FIELDS):
        problems.append(f"{p}: every field must be an integer, got {body!r}")
    elif body["total_cents"] != body["base_cents"] + body["surcharge_cents"]:
        problems.append(f"{p}: total_cents must be base_cents plus surcharge_cents, got {body!r}")

EXTRAS = [
    {"note": "fragile"},
    {"insured": True, "reference": "A-1042"},
    {"weight_kg": 99, "zone_name": "north"},
    {"sender": {"name": "someone", "zone": 9}},
    {"dimensions": [500, 500, 500], "tags": []},
]
for extra in EXTRAS:
    p = random_parcel(rng)
    _, plain = call(p)
    status, body = call({**p, **extra})
    if status != 0 or body != plain:
        problems.append(f"extra fields {extra} must be ignored: expected {plain!r}, got status {status} and {body!r}")

REFUSED = [
    ("text that isn't JSON", "a parcel to zone 2"),
    ("a list", "[1, 1200, 30, 20, 10]"),
    ("zone 9", '{"zone": 9, "weight_g": 1200, "length_cm": 30, "width_cm": 20, "height_cm": 10}'),
    ("a negative weight", '{"zone": 2, "weight_g": -1200, "length_cm": 30, "width_cm": 20, "height_cm": 10}'),
    ("a 151 cm side", '{"zone": 2, "weight_g": 1200, "length_cm": 151, "width_cm": 20, "height_cm": 10}'),
    ("a 40 kg parcel", '{"zone": 2, "weight_g": 40000, "length_cm": 30, "width_cm": 20, "height_cm": 10}'),
]
for name, raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{name}: a refusal must exit with status 2 and write nothing on stdout, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(requests) + len(EXTRAS)} priced and {len(REFUSED)} refused requests")
