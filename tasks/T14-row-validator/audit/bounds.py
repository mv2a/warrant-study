"""X4 (G3, range part): inclusive min and max on integer and number fields, including float bounds and big integers."""

import json

from _audit import e, expect_each
from _cmd import finish

# (rule without name, [(raw JSON value, out of range?)])
CASES = [
    ("integer 16..99", {"type": "integer", "min": 16, "max": 99}, [
        ("16", False), ("99", False), ("15", True), ("100", True), ("16.0", False), ("99.00", False),
        ("15.0", True), ("1E2", True), ("57", False), ("-16", True), ("0", True), ("-0.0", True),
    ]),
    ("number -2.5..7.25", {"type": "number", "min": -2.5, "max": 7.25}, [
        ("-2.5", False), ("7.25", False), ("-2.5000001", True), ("7.2500001", True), ("0", False),
        ("-3", True), ("8", True), ("7", False), ("-2", False), ("7.250", False), ("-25e-1", False), ("1e300", True),
    ]),
    ("integer with fractional bounds 0.5..3.5", {"type": "integer", "min": 0.5, "max": 3.5}, [
        ("0", True), ("1", False), ("3", False), ("4", True), ("3.0", False), ("-1", True),
    ]),
    ("number with only min 0", {"type": "number", "min": 0}, [
        ("0", False), ("-0.0", False), ("-0.001", True), ("1e300", False), ("-1e-300", True), ("0.0", False),
    ]),
    ("integer with only max 0", {"type": "integer", "max": 0}, [
        ("0", False), ("1", True), ("-5", False), ("-1e300", False), ("1.0", True), ("-0.0", False),
    ]),
    ("integer with min equal to max 42", {"type": "integer", "min": 42, "max": 42.0}, [
        ("42", False), ("42.0", False), ("41", True), ("43", True),
    ]),
    ("integer -10..-5", {"type": "integer", "min": -10, "max": -5}, [
        ("-10", False), ("-5", False), ("-4", True), ("-11", True), ("-7", False), ("5", True), ("10", True),
    ]),
    ("big integers", {"type": "integer", "min": -(2**63), "max": 2**63}, [
        (str(2**63), False), (str(2**63 + 1), True), (str(-(2**63)), False), (str(-(2**63) - 1), True),
        (str(10**30), True), ("0", False),
    ]),
    ("number with tiny bounds", {"type": "number", "min": 0.1, "max": 0.3}, [
        ("0.1", False), ("0.3", False), ("0.2", False), ("0.09999999", True), ("0.30000001", True),
    ]),
    ("no bounds at all", {"type": "number"}, [
        ("-1e300", False), ("1e300", False), (str(-(10**40)), False), ("0", False),
    ]),
]

problems = []
count = 0
for label, rule, values in CASES:
    schema = json.dumps([{"name": "q", **rule}])
    rows = ['{"q": %s}' % literal for literal, _ in values]
    expected = [e(i, "q", "range") for i, (_, out) in enumerate(values) if out]
    expect_each(problems, label, schema, rows, expected)
    count += len(values)

finish(problems, f"range ok: {count} values against {len(CASES)} rules")
