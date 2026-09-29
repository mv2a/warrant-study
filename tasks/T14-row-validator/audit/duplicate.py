"""X6 (G4): duplicates in unique fields: equality as in G3, first occurrence clean, only values of the field's type count."""

import json

from _audit import e, expect
from _cmd import finish

NFD = json.dumps("e\u0301")

# (label, rule without name, [raw JSON value or None to leave the field out], expected {row: code})
CASES = [
    ("strings: case and spaces matter", {"type": "string", "unique": True},
     ['"a"', '"b"', '"A"', '"a"', '" a"', '"a "', '"a"', '"b"', '""', '""', '"\\u00e9"', NFD, NFD],
     {3: "duplicate", 6: "duplicate", 7: "duplicate", 9: "duplicate", 12: "duplicate"}),
    ("integers: 5 equals 5.0 and 7.00, 100 equals 1e2", {"type": "integer", "unique": True},
     ["5", "5.0", "7", "7.00", "1e2", "100", "-0.0", "0", "6", "8"],
     {1: "duplicate", 3: "duplicate", 5: "duplicate", 7: "duplicate"}),
    ("numbers: 0 equals -0.0, 0.1 equals 0.10", {"type": "number", "unique": True},
     ["0", "-0.0", "0.1", "0.10", "2.5", "2.50", "25e-1", "0.2", "2", "2.0000001"],
     {1: "duplicate", 3: "duplicate", 5: "duplicate", 6: "duplicate"}),
    ("booleans", {"type": "boolean", "unique": True},
     ["true", "false", "true", "false", "true"],
     {2: "duplicate", 3: "duplicate", 4: "duplicate"}),
    ("an earlier true never makes a later 1 a duplicate", {"type": "number", "unique": True},
     ["true", "1", "false", "0", "1.0", "true"],
     {0: "type", 2: "type", 4: "duplicate", 5: "type"}),
    ("an earlier 1 never makes a later true a duplicate", {"type": "boolean", "unique": True},
     ["1", "true", "1.0", "0", "false", "true", "false"],
     {0: "type", 2: "type", 3: "type", 5: "duplicate", 6: "duplicate"}),
    ("an earlier wrong-typed value never makes a later right one a duplicate", {"type": "string", "unique": True},
     ["1", '"1"', "true", '"true"', "[]", '"[]"', '"1"'],
     {0: "type", 2: "type", 4: "type", 6: "duplicate"}),
    ("an integer field ignores earlier non-integers", {"type": "integer", "unique": True},
     ["4.5", "4.5", '"4"', "4", "true", "1", "4.0"],
     {0: "type", 1: "type", 2: "type", 4: "type", 6: "duplicate"}),
    ("left out and null are never duplicates", {"type": "string", "unique": True},
     [None, "null", None, "null", '"x"', None, "null", '"x"'],
     {7: "duplicate"}),
    ("required and left out: missing, not duplicate", {"type": "integer", "unique": True, "required": True},
     [None, None, "null", "null", "3", "3"],
     {0: "missing", 1: "missing", 2: "missing", 3: "missing", 5: "duplicate"}),
    ("unique set to false allows repeats", {"type": "string", "unique": False},
     ['"z"', '"z"', '"z"'], {}),
    ("unique left out allows repeats", {"type": "integer"},
     ["1", "1", "1.0"], {}),
    ("a repeat far down the table", {"type": "integer", "unique": True},
     [str(n) for n in range(30)] + ["0", "29", "15.0", "30"],
     {30: "duplicate", 31: "duplicate", 32: "duplicate"}),
]

problems = []
count = 0
for label, rule, values, want in CASES:
    schema = json.dumps([{"name": "key", **rule}])
    rows = ", ".join("{}" if literal is None else '{"key": %s}' % literal for literal in values)
    text = '{"schema": %s, "rows": [%s]}' % (schema, rows)
    expected = [e(row, "key", code) for row, code in sorted(want.items())]
    expect(problems, label, text, expected, nrows=len(values))
    count += len(values)

# Uniqueness is per field: the same value in two unique fields is not a duplicate.
schema = [{"name": "left", "type": "string", "unique": True}, {"name": "right", "type": "string", "unique": True}]
rows = [{"left": "p"}, {"right": "p"}, {"left": "q", "right": "q"}, {"left": "p", "right": "q"}]
text = json.dumps({"schema": schema, "rows": rows})
expect(problems, "two unique fields", text, [e(3, "left", "duplicate"), e(3, "right", "duplicate")], nrows=4)

# A row whose other fields are wrong still gets its duplicate, and still counts as an earlier row.
schema = [{"name": "sku", "type": "string", "unique": True}, {"name": "count", "type": "integer", "required": True}]
rows = [{"sku": "k1", "count": "x"}, {"sku": "k1"}, {"sku": "k1", "count": 2}, {"sku": "k2", "count": 1.5}]
text = json.dumps({"schema": schema, "rows": rows})
expect(problems, "duplicates beside other errors", text,
       [e(0, "count", "type"), e(1, "sku", "duplicate"), e(1, "count", "missing"), e(2, "sku", "duplicate"),
        e(3, "count", "type")], nrows=4)

finish(problems, f"duplicate ok: {count + 8} values in {len(CASES) + 2} tables")
