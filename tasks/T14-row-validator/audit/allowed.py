"""X5 (G3, allowed part): exact string matching, numeric value equality and booleans against an allowed list."""

import json

from _audit import e, expect_each
from _cmd import finish

NFD = "n\u0303andu\u0301"  # the same word as "\u00f1and\u00fa" in decomposed code points: not an exact match

# (rule without name, [(raw JSON value, not allowed?)])
CASES = [
    ("strings", {"type": "string", "allowed": ["red", "Green", " blue", "dark  grey", "\u00f1and\u00fa", ""]}, [
        ('"red"', False), ('"Red"', True), ('"RED"', True), ('"red "', True), ('" red"', True),
        ('"Green"', False), ('"green"', True), ('" blue"', False), ('"blue"', True), ('"blue "', True),
        ('"dark  grey"', False), ('"dark grey"', True), ('"\\u00f1and\\u00fa"', False), (json.dumps(NFD), True),
        ('"nandu"', True), ('""', False), ('" "', True), ('"red\\t"', True), ('"redd"', True), ('"re"', True),
    ]),
    ("integers", {"type": "integer", "allowed": [1, 2.0, -3, 0]}, [
        ("1", False), ("1.0", False), ("2", False), ("2.0", False), ("-3", False), ("-3.00", False),
        ("0", False), ("-0.0", False), ("3", True), ("-1", True), ("20", True), ("1e0", False), ("2E0", False),
    ]),
    ("numbers", {"type": "number", "allowed": [0.5, 100, -7.25]}, [
        ("0.5", False), ("0.50", False), ("5e-1", False), ("100", False), ("100.0", False), ("1e2", False),
        ("1E+2", False), ("-7.25", False), ("-7.250", False), ("0.25", True), ("7.25", True), ("99.99999", True),
        ("-100", True), ("0", True), ("0.5000001", True),
    ]),
    ("zero among numbers", {"type": "number", "allowed": [0]}, [
        ("0", False), ("0.0", False), ("-0.0", False), ("-0", False), ("1e-300", True),
    ]),
    ("booleans, only true", {"type": "boolean", "allowed": [True]}, [
        ("true", False), ("false", True), ("true", False),
    ]),
    ("booleans, only false", {"type": "boolean", "allowed": [False]}, [
        ("false", False), ("true", True),
    ]),
    ("booleans, both", {"type": "boolean", "allowed": [False, True]}, [
        ("false", False), ("true", False),
    ]),
    ("one-entry string list", {"type": "string", "allowed": ["only"]}, [
        ('"only"', False), ('"Only"', True), ('"only "', True), ('"onl"', True),
    ]),
]

problems = []
count = 0
for label, rule, values in CASES:
    schema = json.dumps([{"name": "pick", **rule}])
    rows = ['{"pick": %s}' % literal for literal, _ in values]
    expected = [e(i, "pick", "allowed") for i, (_, bad) in enumerate(values) if bad]
    expect_each(problems, label, schema, rows, expected)
    count += len(values)

finish(problems, f"allowed ok: {count} values against {len(CASES)} lists")
