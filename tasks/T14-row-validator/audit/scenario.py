"""X12-X14 (S1, S2, S3): one ROSTER scenario, given as its argument, produces exactly the output the intent states.

The request is sent as hand-formatted JSON with the keys of every rule and row in a different order from
intent.md, which must not change the answer.
"""

import json
import sys

from _audit import canon, run, shape_problem
from _cmd import finish

ROSTER = [
    {"name": "id", "type": "integer", "required": True, "unique": True, "min": 1},
    {"name": "email", "type": "string", "required": True, "unique": True},
    {"name": "age", "type": "integer", "min": 16, "max": 99},
    {"name": "shift", "type": "string", "allowed": ["morning", "evening"]},
    {"name": "lead", "type": "boolean"},
]


def err(row, field, code):
    return {"row": row, "field": field, "code": code}


SCENARIOS = {
    "S1": (
        [
            {"id": 1, "email": "ana@example.org", "age": 34, "shift": "morning", "lead": True},
            {"id": 2, "email": "ben@example.org", "shift": "evening", "badge": "B-17"},
            {"id": 3, "email": "cy@example.org", "age": None, "lead": False},
        ],
        {"valid": True, "errors": []},
    ),
    "S2": (
        [
            {"id": 1, "email": "ana@example.org", "age": 15, "shift": "Morning"},
            {"email": "ben@example.org", "age": "40", "lead": "yes"},
            {"id": 3, "email": None, "age": 58, "shift": "night"},
        ],
        {"valid": False, "errors": [
            err(0, "age", "range"), err(0, "shift", "allowed"), err(1, "id", "missing"), err(1, "age", "type"),
            err(1, "lead", "type"), err(2, "email", "missing"), err(2, "shift", "allowed"),
        ]},
    ),
    "S3": (
        [
            {"id": 7, "email": "ana@example.org"},
            {"id": 8, "email": "ANA@example.org"},
            {"id": 7, "email": "ana@example.org"},
            {"id": 0, "email": "dee@example.org"},
        ],
        {"valid": False, "errors": [err(2, "id", "duplicate"), err(2, "email", "duplicate"), err(3, "id", "range")]},
    ),
}


def reversed_keys(obj):
    return {k: obj[k] for k in reversed(list(obj))}


name = sys.argv[1]
rows, expected = SCENARIOS[name]
schema_text = ",\n    ".join(json.dumps(reversed_keys(rule), separators=(", ", ": ")) for rule in ROSTER)
rows_text = ",\n    ".join(json.dumps(reversed_keys(row), separators=(",", ":")) for row in rows)
text = '{\n  "rows": [\n    %s\n  ],\n  "schema": [\n    %s\n  ]\n}\n' % (rows_text, schema_text)

problems = []
status, out, stderr = run(text)
if status != 0:
    problems.append(f"{name}: exited with status {status}, expected 0 ({stderr.strip()[:60]!r})")
else:
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        body = None
        problems.append(f"{name}: standard output is not one JSON value: {out.strip()[:60]!r}")
    if body is not None:
        problem = shape_problem(body, len(rows))
        if problem:
            problems.append(f"{name}: {problem}")
        elif canon(body) != canon(expected):
            problems.append(f"{name}: expected {canon(expected)}")
            problems.append(f"{name}: got      {canon(body)[:300]}")

finish(problems, f"{name} ok")
