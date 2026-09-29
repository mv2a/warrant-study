"""P2: the three ROSTER scenarios give exactly the stated output."""

from _cmd import call, finish

ROSTER = [
    {"name": "id", "type": "integer", "required": True, "unique": True, "min": 1},
    {"name": "email", "type": "string", "required": True, "unique": True},
    {"name": "age", "type": "integer", "min": 16, "max": 99},
    {"name": "shift", "type": "string", "allowed": ["morning", "evening"]},
    {"name": "lead", "type": "boolean"},
]


def e(row, field, code):
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
            e(0, "age", "range"), e(0, "shift", "allowed"), e(1, "id", "missing"), e(1, "age", "type"),
            e(1, "lead", "type"), e(2, "email", "missing"), e(2, "shift", "allowed"),
        ]},
    ),
    "S3": (
        [
            {"id": 7, "email": "ana@example.org"},
            {"id": 8, "email": "ANA@example.org"},
            {"id": 7, "email": "ana@example.org"},
            {"id": 0, "email": "dee@example.org"},
        ],
        {"valid": False, "errors": [e(2, "id", "duplicate"), e(2, "email", "duplicate"), e(3, "id", "range")]},
    ),
}

problems = []
for name, (rows, expected) in SCENARIOS.items():
    status, body = call({"schema": ROSTER, "rows": rows})
    if status != 0 or body != expected:
        problems.append(f"{name}: expected status 0 and {expected}, got status {status} and {body!r}")

finish(problems, "scenarios ok: S1, S2, S3")
