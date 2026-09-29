"""H1: required fields left out or null get `missing`; optional ones left out or null get nothing (G1)."""

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

# Hand-picked cases: every field carries other rules, so a missing value that were checked
# further would show up as a type, range, allowed or duplicate error.
SCHEMA = [
    {"name": "a", "type": "string", "required": True},
    {"name": "b", "type": "integer", "required": True, "unique": True, "min": 0, "max": 9},
    {"name": "c", "type": "number", "min": 10},
    {"name": "d", "type": "boolean", "unique": True},
    {"name": "e", "type": "string", "allowed": ["x"]},
]
CASES = [
    ({}, ["a", "b"]),
    ({"a": None, "b": None, "c": None, "d": None, "e": None}, ["a", "b"]),
    ({"a": "", "b": 0}, []),
    ({"a": "ok", "b": 1, "c": None, "d": None, "e": None}, []),
    ({"a": "ok", "b": 2, "d": None}, []),
    ({"A": "ok", "B": 3, "b ": 3}, ["a", "b"]),
    ({"a": "ok", "b": None, "c": None}, ["b"]),
    ({"b": 4, "e": None}, ["a"]),
    ({"a": None, "b": 5}, ["a"]),
]
rows = [row for row, _ in CASES]
expected = [e(i, f, "missing") for i, (_, fields) in enumerate(CASES) for f in fields]
status, body = call({"schema": SCHEMA, "rows": rows})
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    problems.append(f"hand-picked rows: expected errors {expected}, got status {status} and {body!r}")

# Present but falsy values are not missing: they are checked like any other value.
status, body = call({"schema": SCHEMA, "rows": [{"a": False, "b": 0}, {"a": 0, "b": 1}, {"a": [], "b": 2}]})
want = [e(0, "a", "type"), e(1, "a", "type"), e(2, "a", "type")]
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), want):
    problems.append(f"false, 0 and [] in a required string field are present values of the wrong type: expected {want}, got status {status} and {body!r}")

# Generated rows, fixed seed: each cell is left out, null, or a good value.
rng = random.Random(1401)
GEN = [
    {"name": "r_name", "type": "string", "required": True},
    {"name": "o_note", "type": "string"},
    {"name": "r_weight", "type": "number", "required": True, "min": 0},
    {"name": "o_ok", "type": "boolean", "required": False},
    {"name": "r_flag", "type": "boolean", "required": True},
    {"name": "o_count", "type": "integer", "unique": True},
]
GOOD = {"r_name": lambda: rng.choice(["x", "y", ""]), "o_note": lambda: "n",
        "r_weight": lambda: rng.choice([0, 1.5, 70]), "o_ok": lambda: rng.random() < 0.5,
        "r_flag": lambda: True, "o_count": None}
rows, expected = [], []
for i in range(160):
    row = {}
    for rule in GEN:
        name = rule["name"]
        pick = rng.choice(["absent", "null", "good"])
        if pick == "null":
            row[name] = None
        elif pick == "good":
            row[name] = i if name == "o_count" else GOOD[name]()
        if pick != "good" and rule.get("required"):
            expected.append(e(i, name, "missing"))
    rows.append(row)
status, body = call({"schema": GEN, "rows": rows})
if status != 0 or not isinstance(body, dict) or not same(body.get("errors"), expected):
    got = body.get("errors") if isinstance(body, dict) else body
    wrong = [x for x in (got or []) if x not in expected][:3] if isinstance(got, list) else got
    problems.append(f"160 generated rows (seed 1401): expected {len(expected)} missing errors, got status {status}; unexpected: {wrong!r}")

finish(problems, "missing ok: 9 hand-picked rows, 3 falsy values, 160 generated rows")
