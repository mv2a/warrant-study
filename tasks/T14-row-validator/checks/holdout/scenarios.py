"""H10: the three ROSTER scenarios, sent as written and re-formatted, give exactly the stated output (S1, S2, S3)."""

import json

from _cmd import call, finish

ROSTER_TEXT = """[{"name": "id", "type": "integer", "required": true, "unique": true, "min": 1},
 {"name": "email", "type": "string", "required": true, "unique": true},
 {"name": "age", "type": "integer", "min": 16, "max": 99},
 {"name": "shift", "type": "string", "allowed": ["morning", "evening"]},
 {"name": "lead", "type": "boolean"}]"""

SCENARIOS = {
    "S1": ('[{"id": 1, "email": "ana@example.org", "age": 34, "shift": "morning", "lead": true}, '
           '{"id": 2, "email": "ben@example.org", "shift": "evening", "badge": "B-17"}, '
           '{"id": 3, "email": "cy@example.org", "age": null, "lead": false}]',
           '{"valid": true, "errors": []}'),
    "S2": ('[{"id": 1, "email": "ana@example.org", "age": 15, "shift": "Morning"}, '
           '{"email": "ben@example.org", "age": "40", "lead": "yes"}, '
           '{"id": 3, "email": null, "age": 58, "shift": "night"}]',
           '{"valid": false, "errors": [{"row": 0, "field": "age", "code": "range"}, '
           '{"row": 0, "field": "shift", "code": "allowed"}, {"row": 1, "field": "id", "code": "missing"}, '
           '{"row": 1, "field": "age", "code": "type"}, {"row": 1, "field": "lead", "code": "type"}, '
           '{"row": 2, "field": "email", "code": "missing"}, {"row": 2, "field": "shift", "code": "allowed"}]}'),
    "S3": ('[{"id": 7, "email": "ana@example.org"}, {"id": 8, "email": "ANA@example.org"}, '
           '{"id": 7, "email": "ana@example.org"}, {"id": 0, "email": "dee@example.org"}]',
           '{"valid": false, "errors": [{"row": 2, "field": "id", "code": "duplicate"}, '
           '{"row": 2, "field": "email", "code": "duplicate"}, {"row": 3, "field": "id", "code": "range"}]}'),
}


def reversed_keys(value):
    if isinstance(value, dict):
        return {k: reversed_keys(value[k]) for k in reversed(list(value))}
    if isinstance(value, list):
        return [reversed_keys(v) for v in value]
    return value


problems = []
for name, (rows_text, output_text) in SCENARIOS.items():
    expected = json.loads(output_text)
    as_written = '{"schema": %s, "rows": %s}' % (ROSTER_TEXT, rows_text)
    request = json.loads(as_written)
    variants = {
        "as written": as_written,
        "on one line": json.dumps(request, separators=(",", ":")),
        "with every key order reversed": json.dumps(reversed_keys(request), indent=2),
    }
    for how, raw in variants.items():
        status, body = call(raw=raw)
        if status != 0 or body != expected:
            problems.append(f"{name} {how}: expected status 0 and {output_text}, got status {status} and {body!r}")

finish(problems, "scenarios ok: S1, S2, S3, three ways each")
