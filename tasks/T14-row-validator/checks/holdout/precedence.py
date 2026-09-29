"""H7: a field of a row gets at most one error, the first in the order missing, type, range, allowed, duplicate (C2)."""

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
F = {"name": "f", "type": "integer", "required": True, "unique": True, "min": 0, "max": 9, "allowed": [1, 2, 3, 20]}
S = {"name": "s", "type": "string", "required": True, "unique": True, "allowed": ["a", "b"]}
CASES = [
    ({}, "missing", "missing"),
    ({"other": None}, "missing", "missing"),
    ({"f": "1", "s": 1}, "type", "type"),
    ({"f": 1.5, "s": True}, "type", "type"),
    ({"f": 20, "s": "c"}, "range", "allowed"),
    ({"f": 20, "s": "c"}, "range", "allowed"),
    ({"f": -1, "s": "A"}, "range", "allowed"),
    ({"f": 5, "s": "a"}, "allowed", None),
    ({"f": 5, "s": "a"}, "allowed", "duplicate"),
    ({"f": 1, "s": "b"}, None, None),
    ({"f": 1, "s": "b"}, "duplicate", "duplicate"),
    ({"f": 30, "s": "A"}, "range", "allowed"),
    ({"f": [1], "s": ["a"]}, "type", "type"),
    ({"f": -1}, "range", "missing"),
    ({"f": 1, "s": "b"}, "duplicate", "duplicate"),
]
rows = [row for row, _, _ in CASES]
expected = [e(i, name, code) for i, (_, fc, sc) in enumerate(CASES) for name, code in (("f", fc), ("s", sc)) if code]
status, body = call({"schema": [F, S], "rows": rows})
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    got = body.get("errors") if isinstance(body, dict) else body
    diff = ([x for x in got if x not in expected] + [f"missing {x}" for x in expected if x not in got]) if isinstance(got, list) else [got]
    problems.append(f"hand-picked rows: errors differ: {diff[:6]!r}")

# Generated rows, fixed seed: the expected code comes from the order in C2.
rng = random.Random(1406)
POOL = ["absent", "x", 2.5, [2], -3, 12, 20, 4, 6, 1, 2, 3, 0, 8]


def first_code(value, seen):
    if value == "absent":
        return "missing"
    if not isinstance(value, (int, float)) or value != int(value):
        return "type"
    if value < 0 or value > 9:
        return "range"
    if value not in (1, 2, 3, 20):
        return "allowed"
    if value in seen:
        return "duplicate"
    seen.add(value)
    return None


for n in range(5):
    seen = set()
    rows, expected = [], []
    for i in range(80):
        value = rng.choice(POOL)
        rows.append({} if value == "absent" else {"f": value})
        code = first_code(value, seen)
        if code:
            expected.append(e(i, "f", code))
    status, body = call({"schema": [F], "rows": rows})
    got = body.get("errors") if isinstance(body, dict) else None
    if status != 0 or not same(got, expected):
        if isinstance(got, list):
            cells = [(x.get("row"), x.get("field")) for x in got if isinstance(x, dict)]
            if len(cells) != len(set(cells)):
                problems.append(f"generated set {n} (seed 1406): some field of some row got more than one error")
                continue
        diff = ([x for x in got if x not in expected][:2] + [f"missing {x}" for x in expected if x not in got][:2]) if isinstance(got, list) else [got]
        problems.append(f"generated set {n} (seed 1406): errors differ: {diff!r}")

finish(problems, "precedence ok: 15 hand-picked rows, 5 generated sets of 80 rows")
