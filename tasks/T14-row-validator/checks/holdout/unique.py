"""H4: `duplicate` goes on every later repeat of a value in a unique field, never on the first (G4)."""

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
D = "duplicate"
SCHEMA = [
    {"name": "id", "type": "integer", "unique": True},
    {"name": "code", "type": "string", "unique": True},
    {"name": "flag", "type": "boolean", "unique": True},
    {"name": "score", "type": "number", "unique": True},
    {"name": "tag", "type": "string"},
]
ROWS = [
    ({"id": 1, "code": "a", "flag": True, "score": 2.5, "tag": "t"}, []),
    ({"id": 2, "code": "A", "flag": False, "score": 2, "tag": "t"}, []),
    ({"id": 1.0, "code": "a", "flag": True, "score": 2.0, "tag": "t"}, [("id", D), ("code", D), ("flag", D), ("score", D)]),
    ({"id": 1, "code": "a ", "flag": False}, [("id", D), ("flag", D)]),
    ({"id": None, "code": None, "flag": None, "score": None}, []),
    ({}, []),
    ({"id": None, "code": None}, []),
    ({"id": "3", "code": 3}, [("id", "type"), ("code", "type")]),
    ({"id": 3, "code": "3"}, []),
    ({"id": True, "score": True}, [("id", "type"), ("score", "type")]),
    ({"id": 1.5, "score": False}, [("id", "type"), ("score", "type")]),
    ({"score": 1, "id": 0}, []),
    ({"score": 0.0, "id": 4}, []),
    ({"score": 1.0, "id": 3.0}, [("id", D), ("score", D)]),
    ({"score": -0.0, "id": -0.0}, [("id", D), ("score", D)]),
    ({"code": "a", "tag": "t"}, [("code", D)]),
    # A composed accent and the same letter as base plus combining accent are different strings.
    ({"code": "ça"}, []),
    ({"code": "ça"}, []),
    ({"code": "ça"}, [("code", D)]),
]
rows = [row for row, _ in ROWS]
expected = [e(i, f, c) for i, (_, errs) in enumerate(ROWS) for f, c in errs]
status, body = call({"schema": SCHEMA, "rows": rows})
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    got = body.get("errors") if isinstance(body, dict) else body
    diff = ([x for x in got if x not in expected] + [f"missing {x}" for x in expected if x not in got]) if isinstance(got, list) else [got]
    problems.append(f"hand-picked rows: errors differ: {diff[:6]!r}")

# Generated rows, fixed seed: small pools so values repeat often.
rng = random.Random(1404)
GEN = [
    {"name": "n", "type": "integer", "unique": True},
    {"name": "s", "type": "string", "unique": True},
    {"name": "x", "type": "number", "unique": True},
]
seen = {"n": [], "s": [], "x": []}
rows, expected = [], []
for i in range(300):
    row = {}
    for rule in GEN:
        name = rule["name"]
        pick = rng.random()
        if pick < 0.1:
            continue
        if pick < 0.2:
            row[name] = None
            continue
        if name == "n":
            v = rng.randint(0, 150)
            v = float(v) if rng.random() < 0.3 else v
        elif name == "s":
            v = rng.choice(["k", "K", "k2", "q"]) + str(rng.randint(0, 40))
        else:
            v = rng.randint(0, 120) / 4
        row[name] = v
        if any(v == old for old in seen[name]):
            expected.append(e(i, name, D))
        else:
            seen[name].append(v)
    rows.append(row)
status, body = call({"schema": GEN, "rows": rows})
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    got = body.get("errors") if isinstance(body, dict) else body
    diff = ([x for x in got if x not in expected][:2] + [f"missing {x}" for x in expected if x not in got][:2]) if isinstance(got, list) else [got]
    problems.append(f"300 generated rows (seed 1404, {len(expected)} duplicates): errors differ: {diff!r}")

# A field that is not unique never reports duplicates.
status, body = call({"schema": [{"name": "v", "type": "integer"}], "rows": [{"v": 1}] * 25})
if status != 0 or body != {"valid": True, "errors": []}:
    problems.append(f"25 equal values in a field that is not unique must be valid, got status {status} and {body!r}")

finish(problems, f"unique ok: 19 hand-picked rows, 300 generated rows, 1 non-unique field")
