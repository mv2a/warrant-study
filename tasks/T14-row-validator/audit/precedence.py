"""X8 (C2): one error at most per field of a row, the first that applies in the order missing, type, range, allowed, duplicate."""

import json

from _audit import e, expect
from _cmd import finish

# (label, rule without name, [raw JSON value or None to leave the field out], expected {row: code})
CASES = [
    ("integer: required, unique, 10..20, allowed 10/12/14/30",
     {"type": "integer", "required": True, "unique": True, "min": 10, "max": 20, "allowed": [10, 12, 14, 30]},
     [None, "null", '"12"', "12.5", "true", "30", "9", "11", "12", "12.0", "30", "9", "11", "14", "14", '"14"', "[]"],
     {0: "missing", 1: "missing", 2: "type", 3: "type", 4: "type", 5: "range", 6: "range", 7: "allowed",
      9: "duplicate", 10: "range", 11: "range", 12: "allowed", 14: "duplicate", 15: "type", 16: "type"}),
    ("string: required, unique, allowed x/y",
     {"type": "string", "required": True, "unique": True, "allowed": ["x", "y"]},
     ["null", "5", '"z"', '"z"', '"x"', '"x"', '"X"', None, '["x"]', '"y"', '"y"'],
     {0: "missing", 1: "type", 2: "allowed", 3: "allowed", 5: "duplicate", 6: "allowed", 7: "missing",
      8: "type", 10: "duplicate"}),
    ("number: optional, unique, 0..1",
     {"type": "number", "unique": True, "min": 0, "max": 1},
     ["null", "1.5", "1.5", "0.5", "0.50", "false", "-0.0", "0", None, "-1", "-1", "1"],
     {1: "range", 2: "range", 4: "duplicate", 5: "type", 7: "duplicate", 9: "range", 10: "range"}),
    ("boolean: required, unique, allowed true",
     {"type": "boolean", "required": True, "unique": True, "allowed": [True]},
     ["false", "false", "true", "true", "1", "null", '"true"'],
     {0: "allowed", 1: "allowed", 3: "duplicate", 4: "type", 5: "missing", 6: "type"}),
    ("integer: range and allowed both fail, range wins",
     {"type": "integer", "min": 0, "max": 5, "allowed": [1, 2]},
     ["-1", "6", "3", "1", "2.0", "7.5", '"1"'],
     {0: "range", 1: "range", 2: "allowed", 5: "type", 6: "type"}),
    ("number: a required null with bounds is missing only",
     {"type": "number", "required": True, "min": 5, "allowed": [6]},
     ["null", None, "4", "5", "6"],
     {0: "missing", 1: "missing", 2: "range", 3: "allowed"}),
]

problems = []
count = 0
for label, rule, values, want in CASES:
    schema = json.dumps([{"name": "f", **rule}])
    rows = ", ".join("{}" if literal is None else '{"f": %s}' % literal for literal in values)
    text = '{"schema": %s, "rows": [%s]}' % (schema, rows)
    expected = [e(row, "f", code) for row, code in sorted(want.items())]
    body = expect(problems, label, text, expected, nrows=len(values))
    if body is not None:
        pairs = [(err["row"], err["field"]) for err in body["errors"]]
        if len(pairs) != len(set(pairs)):
            problems.append(f"{label}: some field of a row got more than one error")
    count += len(values)

# Several fields in one row, each with a different winner.
schema = [
    {"name": "a", "type": "integer", "required": True, "min": 3},
    {"name": "b", "type": "string", "allowed": ["on"], "unique": True},
    {"name": "c", "type": "number", "max": 1, "allowed": [0.5], "unique": True},
    {"name": "d", "type": "boolean", "required": True, "allowed": [False]},
]
rows = [
    {"a": 3, "b": "on", "c": 0.5, "d": False},
    {"a": None, "b": "off", "c": 2, "d": "false"},
    {"a": "4", "b": "on", "c": 0.5, "d": True},
    {"a": 1, "b": 1, "c": 0.25},
]
expect(problems, "mixed winners in one row", json.dumps({"schema": schema, "rows": rows}),
       [e(1, "a", "missing"), e(1, "b", "allowed"), e(1, "c", "range"), e(1, "d", "type"),
        e(2, "a", "type"), e(2, "b", "duplicate"), e(2, "c", "duplicate"), e(2, "d", "allowed"),
        e(3, "a", "range"), e(3, "b", "type"), e(3, "c", "allowed"), e(3, "d", "missing")], nrows=4)

finish(problems, f"precedence ok: {count + 4} rows")
