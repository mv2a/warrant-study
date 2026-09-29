"""X2 (G1): required fields left out or null get `missing`; optional ones left out or null get nothing at all."""

import json

from _audit import e, expect_each
from _cmd import finish

problems = []

SCHEMA = [
    {"name": "r_s", "type": "string", "required": True},
    {"name": "r_i", "type": "integer", "required": True},
    {"name": "r_b", "type": "boolean", "required": True},
    {"name": "r_n", "type": "number", "required": True},
    {"name": "o_s", "type": "string", "allowed": ["x"]},
    {"name": "o_i", "type": "integer", "min": 5, "max": 6, "unique": True},
    {"name": "o_b", "type": "boolean", "required": False},
    {"name": "o_n", "type": "number", "min": 100, "unique": False},
]
REQUIRED = ["r_s", "r_i", "r_b", "r_n"]
OPTIONAL_NULLS = {"o_s": None, "o_i": None, "o_b": None, "o_n": None}
FULL = {"r_s": "v", "r_i": 1, "r_b": True, "r_n": 0.5}

# (row, [field that is missing, or (field, code)])
CASES = [
    ({}, REQUIRED),
    ({**{k: None for k in REQUIRED}, **OPTIONAL_NULLS}, REQUIRED),
    ({"r_s": "", "r_i": 0, "r_b": False, "r_n": 0}, []),
    ({"r_s": " ", "r_i": 0.0, "r_b": False, "r_n": -0.0, **OPTIONAL_NULLS}, []),
    ({"r_s": [], "r_i": {}, "r_b": [], "r_n": {}}, [("r_s", "type"), ("r_i", "type"), ("r_b", "type"), ("r_n", "type")]),
    ({"r_s": "v", "r_b": True, "r_n": 2}, ["r_i"]),
    ({**FULL, "r_n": None}, ["r_n"]),
    ({"r_s": None, "r_i": 3, "r_b": None, "r_n": 1}, ["r_s", "r_b"]),
    ({"R_S": "v", "r_i ": 1, "r_b": True, "r_n": 1}, ["r_s", "r_i"]),
    ({**FULL, **OPTIONAL_NULLS}, []),
    (dict(FULL), []),
    ({**FULL, "o_i": None}, []),
    ({**FULL, "o_s": None, "o_n": None, "o_b": None}, []),
]

rows, expected = [], []
for index, (row, want) in enumerate(CASES):
    rows.append(json.dumps(row))
    for item in want:
        field, code = item if isinstance(item, tuple) else (item, "missing")
        expected.append(e(index, field, code))
expect_each(problems, "eight-field table", json.dumps(SCHEMA), rows, expected)

# A long table: the required field is present every third row, left out or null otherwise.
schema = [{"name": "who", "type": "string", "required": True}, {"name": "memo", "type": "string"}]
rows, expected = [], []
for index in range(45):
    kind = index % 3
    if kind == 0:
        rows.append(json.dumps({"who": f"p{index}", "memo": None}))
    elif kind == 1:
        rows.append(json.dumps({"memo": "left out"}))
        expected.append(e(index, "who", "missing"))
    else:
        rows.append(json.dumps({"who": None}))
        expected.append(e(index, "who", "missing"))
expect_each(problems, "45 rows alternating present, left out and null", json.dumps(schema), rows, expected)

# A schema with only optional fields accepts rows that give nothing.
schema = [{"name": "a", "type": "integer", "min": 1}, {"name": "b", "type": "boolean", "unique": True}]
rows = [json.dumps(row) for row in ({}, {"a": None}, {"b": None}, {"a": None, "b": None}, {})]
expect_each(problems, "optional fields only", json.dumps(schema), rows, [])

finish(problems, f"missing ok: {len(CASES)} rows of an eight-field table, a 45-row table, an optional-only table")
