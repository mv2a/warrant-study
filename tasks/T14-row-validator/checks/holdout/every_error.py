"""H5: every problem in every row is reported, and fields the schema does not name are ignored (G5)."""

import json
import random

from _cmd import call, finish


def same(got, expected):
    """Equal as collections of errors: this check is not about their order (C3 is)."""
    key = lambda x: json.dumps(x, sort_keys=True)
    return isinstance(got, list) and sorted(map(key, got)) == sorted(map(key, expected))


def e(row, field, code):
    return {"row": row, "field": field, "code": code}


problems = []
SCHEMA = [
    {"name": "a", "type": "string", "required": True},
    {"name": "b", "type": "integer"},
    {"name": "c", "type": "number", "min": 0, "max": 10},
    {"name": "d", "type": "string", "allowed": ["p", "q"]},
    {"name": "f", "type": "boolean", "required": True},
    {"name": "g", "type": "integer", "min": 1},
]
# A row where every field is wrong, repeated 250 times: 6 errors per row, 1500 in all.
BAD = {"b": "two", "c": 11, "d": "r", "g": 0}
BAD_CODES = [("a", "missing"), ("b", "type"), ("c", "range"), ("d", "allowed"), ("f", "missing"), ("g", "range")]
status, body = call({"schema": SCHEMA, "rows": [dict(BAD) for _ in range(250)]})
expected = [e(i, f, c) for i in range(250) for f, c in BAD_CODES]
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    n = len(body.get("errors", [])) if isinstance(body, dict) and isinstance(body.get("errors"), list) else body
    problems.append(f"250 rows with 6 bad fields each: expected all 1500 errors, got status {status} and {n!r} errors")

# One bad cell in the last of 600 rows.
good = {"a": "x", "b": 1, "c": 5, "d": "p", "f": True, "g": 3}
rows = [dict(good) for _ in range(600)]
rows[-1]["c"] = -0.5
status, body = call({"schema": SCHEMA, "rows": rows})
if status != 0 or body != {"valid": False, "errors": [e(599, "c", "range")]}:
    problems.append(f"a single bad cell in the last of 600 rows must be reported, got status {status} and {body!r}")

# Fields the schema does not name are ignored, whatever they hold.
extra = dict(good, A=None, B="two", extra=[1, 2], nested={"a": None}, **{"": 0, "c ": 99, "D": "r", "missing": None})
status, body = call({"schema": SCHEMA, "rows": [extra, dict(good, zzz=None)]})
if status != 0 or body != {"valid": True, "errors": []}:
    problems.append(f"fields not named in the schema must be ignored, got status {status} and {body!r}")

# Generated rows, fixed seed: each cell good or bad at random.
rng = random.Random(1405)
CHOICES = {
    "a": [("s", None), (7, "type"), ("absent", "missing")],
    "b": [(3, None), (3.5, "type"), ("3", "type"), ("absent", None)],
    "c": [(0, None), (9.5, None), (10.5, "range"), (-1, "range"), ("0", "type")],
    "d": [("p", None), ("q", None), ("P", "allowed"), ("absent", None)],
    "f": [(False, None), (0, "type"), ("absent", "missing")],
    "g": [(1, None), (0, "range"), (2, None), ([], "type")],
}
rows, expected = [], []
for i in range(400):
    row = {}
    for rule in SCHEMA:
        value, code = rng.choice(CHOICES[rule["name"]])
        if value != "absent":
            row[rule["name"]] = value
        if code:
            expected.append(e(i, rule["name"], code))
    if rng.random() < 0.3:
        row["note"] = rng.choice(["x", None, 5])
    rows.append(row)
status, body = call({"schema": SCHEMA, "rows": rows})
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    got = body.get("errors") if isinstance(body, dict) else body
    diff = ([x for x in got if x not in expected][:2] + [f"missing {x}" for x in expected if x not in got][:2]) if isinstance(got, list) else [got]
    problems.append(f"400 generated rows (seed 1405, {len(expected)} errors): errors differ: {diff!r}")

finish(problems, "every error ok: 1500-error table, last-row error, ignored fields, 400 generated rows")
