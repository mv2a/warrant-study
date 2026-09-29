"""X3 (G2): which JSON values each of the four field types accepts, written as raw JSON text."""

import json

from _audit import e, expect_each
from _cmd import finish

# (raw JSON text of the value, whether it holds the type)
CASES = {
    "string": [
        ('"abc"', True), ('""', True), ('"4"', True), ('"true"', True), ('"null"', True), ('"  "', True),
        ('"\\u00e9t\\u00e9"', True),
        ("4", False), ("4.0", False), ("0", False), ("-1.5", False), ("true", False), ("false", False),
        ("[]", False), ("{}", False), ('["a"]', False), ('{"a": "b"}', False),
    ],
    "boolean": [
        ("true", True), ("false", True),
        ("0", False), ("1", False), ("1.0", False), ('"true"', False), ('"false"', False), ('""', False),
        ("[]", False), ("{}", False), ("[true]", False), ('{"v": false}', False),
    ],
    "number": [
        ("0", True), ("-7", True), ("3.25", True), ("-0.0", True), ("1E2", True), ("2.5e-3", True),
        ("1e300", True), ("-1e-300", True), ("123456789012345678901234567890", True), ("0.000", True),
        ("true", False), ("false", False), ('"3"', False), ('"3.5"', False), ('""', False),
        ("[]", False), ("[1]", False), ("{}", False), ('{"n": 1}', False),
    ],
    "integer": [
        ("4", True), ("4.0", True), ("4.00", True), ("-0.0", True), ("0", True), ("-12", True), ("-12.0", True),
        ("1e2", True), ("1.5E1", True), ("-3.0e0", True), ("1e300", True),
        ("123456789012345678901234567890", True),
        ("4.5", False), ("0.1", False), ("-2.5", False), ("25e-1", False), ("1e-1", False), ("-0.5", False),
        ("true", False), ("false", False), ('"4"', False), ('"4.0"', False), ('""', False),
        ("[]", False), ("[4]", False), ("{}", False), ('{"i": 4}', False),
    ],
}

problems = []
count = 0
for kind, cases in CASES.items():
    schema = json.dumps([{"name": "v", "type": kind}])
    rows = ['{"v": %s}' % literal for literal, _ in cases]
    expected = [e(i, "v", "type") for i, (_, ok) in enumerate(cases) if not ok]
    expect_each(problems, f"{kind} field", schema, rows, expected)
    count += len(cases)

# The same values in a required field: a wrong type is a type error, never missing.
schema = json.dumps([{"name": "v", "type": "integer", "required": True}])
rows = ['{"v": false}', '{"v": 0}', '{"v": ""}', '{"v": 0.0}', '{"v": []}']
expect_each(problems, "required integer field", schema, rows, [e(0, "v", "type"), e(2, "v", "type"), e(4, "v", "type")])

finish(problems, f"types ok: {count} values across the four types")
