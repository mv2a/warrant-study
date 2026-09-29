"""X7 (G5): every problem in every row is reported, and fields the schema does not name are ignored."""

import json
import random

from _audit import e, expect
from _cmd import finish

problems = []

# 1. Every field of every row is wrong, one way or another: 5 rows x 6 fields = 30 errors.
schema = [
    {"name": "code", "type": "string", "required": True, "allowed": ["A", "B"]},
    {"name": "qty", "type": "integer", "min": 1, "max": 500},
    {"name": "price", "type": "number", "min": 0},
    {"name": "paid", "type": "boolean", "required": True},
    {"name": "ref", "type": "string", "unique": True},
    {"name": "note", "type": "string"},
]
first = {"code": "A", "qty": 1, "price": 0, "paid": True, "ref": "R", "note": ""}
bad_rows = [
    {"code": "a", "qty": 0, "price": -1, "paid": "no", "ref": "R", "note": 1},
    {"qty": 2.5, "price": True, "paid": None, "ref": 7, "note": []},
    {"code": None, "qty": 501, "price": "0", "ref": "R", "note": {}},
    {"code": 5, "qty": "3", "price": -0.01, "paid": 0, "ref": "R", "note": False},
    {"code": "C", "qty": -1, "price": [0], "ref": "R", "note": 0.5},
]
codes = [
    ["allowed", "range", "range", "type", "duplicate", "type"],
    ["missing", "type", "type", "missing", "type", "type"],
    ["missing", "range", "type", "missing", "duplicate", "type"],
    ["type", "type", "range", "type", "duplicate", "type"],
    ["allowed", "range", "type", "missing", "duplicate", "type"],
]
rows = [first] + bad_rows
expected = [e(r + 1, rule["name"], codes[r][f]) for r in range(5) for f, rule in enumerate(schema)]
expect(problems, "every field of every row wrong", json.dumps({"schema": schema, "rows": rows}), expected, nrows=6)

# 2. Fields the schema does not name are ignored, whatever they hold.
extra_rows = [
    {**first, "Code": 5, "QTY": "x", "extra": {"nested": [1, 2]}, "": None, "ref": "R1"},
    {**first, "paid ": "no", "unknown": [], "ref": "R2", "price": 3, "zzz": True},
]
expect(problems, "extra fields ignored", json.dumps({"schema": schema, "rows": extra_rows}), [], nrows=2)

# 3. A 300-row table with problems scattered by a seeded generator; each field's outcome is known by construction.
MENUS = {
    "code": [("A", None), ("B", None), ("b", "allowed"), ("A ", "allowed"), (7, "type"), ("LEAVE", "missing"),
             (None, "missing")],
    "qty": [(1, None), (500, None), (250.0, None), (0, "range"), (501, "range"), (2.5, "type"), ("3", "type"),
            ("LEAVE", None), (None, None)],
    "price": [(0, None), (19.99, None), (-0.01, "range"), (True, "type"), ("LEAVE", None)],
    "paid": [(True, None), (False, None), ("no", "type"), (0, "type"), ("LEAVE", "missing"), (None, "missing")],
    "note": [("", None), ("x", None), (["x"], "type"), ({}, "type"), (None, None), ("LEAVE", None)],
}
rng = random.Random(44_021_613)
rows, expected, seen_refs = [], [], []
for index in range(300):
    row = {}
    for rule in schema:
        name = rule["name"]
        if name == "ref":
            roll = rng.random()
            if roll < 0.15 and seen_refs:
                row["ref"] = rng.choice(seen_refs)
                expected.append(e(index, "ref", "duplicate"))
            elif roll < 0.25:
                pass
            else:
                value = f"R{index}"
                row["ref"] = value
                seen_refs.append(value)
            continue
        value, code = rng.choice(MENUS[name])
        if value != "LEAVE":
            row[name] = value
        if code:
            expected.append(e(index, name, code))
    if rng.random() < 0.2:
        row["comment"] = rng.choice([1, "x", None, [], {"deep": True}])
    rows.append(row)
body = expect(problems, "300 generated rows (seed 44021613)", json.dumps({"schema": schema, "rows": rows}), expected,
              nrows=300)
if body is not None and problems and body["errors"]:
    last = max(err["row"] for err in body["errors"])
    problems.append(f"expected {len(expected)} errors up to row {expected[-1]['row']}, got {len(body['errors'])} up to row {last}")

finish(problems, f"every error ok: 30-error table, extra fields, 300 rows with {len(expected)} errors")
