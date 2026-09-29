"""H8: errors are listed by row, then by the field's position in the schema (C3)."""

import random

from _cmd import call, finish


def e(row, field, code):
    return {"row": row, "field": field, "code": code}


problems = []

# Field order in the schema is neither alphabetical nor the order keys appear in the rows.
SCHEMA = [
    {"name": "zeta", "type": "integer", "required": True},
    {"name": "alpha", "type": "string", "unique": True},
    {"name": "Mid", "type": "number", "max": 1},
    {"name": "beta", "type": "boolean", "required": True},
    {"name": "_x", "type": "string", "allowed": ["y"]},
]
ROWS = [
    {"_x": "n", "beta": 1, "Mid": 2, "alpha": "a"},
    {"zeta": 1, "alpha": "b", "beta": True},
    {"_x": "y", "alpha": "a", "zeta": "1", "beta": False, "Mid": 5},
    {"beta": True, "zeta": 3},
    {"alpha": "b", "_x": 0},
]
EXPECTED = [
    e(0, "zeta", "missing"), e(0, "Mid", "range"), e(0, "beta", "type"), e(0, "_x", "allowed"),
    e(2, "zeta", "type"), e(2, "alpha", "duplicate"), e(2, "Mid", "range"),
    e(4, "zeta", "missing"), e(4, "alpha", "duplicate"), e(4, "beta", "missing"), e(4, "_x", "type"),
]
status, body = call({"schema": SCHEMA, "rows": ROWS})
if status != 0 or not isinstance(body, dict) or body.get("errors") != EXPECTED:
    problems.append(f"hand-picked rows: expected {EXPECTED}, got status {status} and {body!r}")

# Generated schemas and rows, fixed seed: shuffled field order, every code possible.
rng = random.Random(1407)
NAMES = ["id", "Name", "zip", "_code", "amount", "b2", "Qty", "flag", "a", "Zed", "note", "m"]
KINDS = {
    "integer": ({"min": 0, "max": 50}, [(5, None), (-1, "range"), (51, "range"), ("5", "type"), (6, "allowed")], [5, 7, 51]),
    "string": ({"allowed": ["on", "off"]}, [("on", None), ("off", None), ("ON", "allowed"), (1, "type")], ["on", "off"]),
    "number": ({"max": 2.5}, [(2.25, None), (2.75, "range"), ("2", "type"), (-9, None)], None),
    "boolean": ({}, [(True, None), (False, None), ("true", "type")], None),
}
for n in range(12):
    names = rng.sample(NAMES, rng.randint(3, 7))
    schema = []
    for name in names:
        kind = rng.choice(list(KINDS))
        extra, _, allowed = KINDS[kind]
        rule = {"name": name, "type": kind, **extra}
        if kind == "integer":
            rule["allowed"] = allowed
        rule["required"] = rng.random() < 0.4
        rule["unique"] = kind == "string" and rng.random() < 0.5
        schema.append(rule)
    seen = {rule["name"]: set() for rule in schema}
    rows, expected = [], []
    for i in range(40):
        row = {}
        for rule in rng.sample(schema, len(schema)):
            name = rule["name"]
            if rng.random() < 0.15:
                code = "missing" if rule["required"] else None
            else:
                value, code = rng.choice(KINDS[rule["type"]][1])
                row[name] = value
                if code is None and rule["unique"]:
                    code = "duplicate" if value in seen[name] else None
                    seen[name].add(value)
            if code:
                expected.append((i, [r["name"] for r in schema].index(name), e(i, name, code)))
        rows.append(row)
    expected = [x for _, _, x in sorted(expected, key=lambda t: (t[0], t[1]))]
    status, body = call({"schema": schema, "rows": rows})
    got = body.get("errors") if isinstance(body, dict) else None
    if status != 0 or got != expected:
        same_set = isinstance(got, list) and sorted(map(str, got)) == sorted(map(str, expected))
        what = "the right errors in the wrong order" if same_set else "different errors"
        problems.append(f"generated schema {n} (seed 1407, fields {names}): {what}")

finish(problems, "order ok: 5 hand-picked rows, 12 generated schemas of 40 rows")
