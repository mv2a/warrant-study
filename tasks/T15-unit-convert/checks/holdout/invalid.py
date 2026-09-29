"""H7: malformed requests are refused, never converted, while the allowed edge forms are accepted (C4)."""

import json

from _cmd import call, finish

GOOD = {"value": "3", "from": "m", "to": "cm", "places": 1}


def with_field(name, value):
    request = dict(GOOD)
    request[name] = value
    return json.dumps(request)


def without_field(name):
    return json.dumps({key: value for key, value in GOOD.items() if key != name})


INVALID = [
    ("text that is not JSON", "three metres"),
    ("empty input", ""),
    ("a JSON list", '["3", "m", "cm", 1]'),
    ("a JSON string", '"3 m"'),
    ("JSON null", "null"),
    ("a truncated object", '{"value": "3", "from": "m"'),
    ("a missing value", without_field("value")),
    ("a missing from", without_field("from")),
    ("a missing to", without_field("to")),
    ("a missing places", without_field("places")),
    ("an extra field", with_field("note", "x")),
    ("an extra field named unit", with_field("unit", "cm")),
    ("value as a JSON number", with_field("value", 3)),
    ("value as a JSON fraction", with_field("value", 3.5)),
    ("value null", with_field("value", None)),
    ("value true", with_field("value", True)),
    ("value as a list", with_field("value", ["3"])),
]
for text in ["", "-1", "+1", "-0", "1e3", "1E3", "1.5e2", ".5", "5.", " 5", "5 ", "5\n", "1,5", "1 000",
             "1_000", "1/2", "1..2", "1.2.3", "0x10", "NaN", "inf", "five", "５", "٣", "5m"]:
    INVALID.append((f"value {text!r}", with_field("value", text)))
for field in ("from", "to"):
    for bad in (None, 1, True, ["m"], {"unit": "m"}):
        INVALID.append((f"{field} {bad!r}", with_field(field, bad)))
for bad in (13, 100, -1, 2.5, 2.0, 1e1, "2", None, True, False, [2]):
    INVALID.append((f"places {bad!r}", with_field("places", bad)))
INVALID.append(("places written as 2.0", '{"value": "3", "from": "m", "to": "cm", "places": 2.0}'))
INVALID.append(("places written as 2e0", '{"value": "3", "from": "m", "to": "cm", "places": 2e0}'))

ACCEPTED = [
    ({"value": "0", "from": "m", "to": "cm", "places": 0}, "0"),
    ({"value": "007.50", "from": "m", "to": "cm", "places": 0}, "750"),
    ({"value": "3", "from": "m", "to": "cm", "places": 12}, "300.000000000000"),
    ({"value": "0.000", "from": "l", "to": "ml", "places": 1}, "0.0"),
    ({"value": "10", "from": "kg", "to": "g", "places": 0}, "10000"),
    ({"places": 2, "to": "yd", "from": "ft", "value": "3"}, "1.00"),
]

problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    if status != 2 or (isinstance(body, dict) and "value" in body):
        problems.append(f"{name}: expected a refusal (status 2, no result), got status {status} and {body!r}")
for request, want in ACCEPTED:
    status, body = call(request)
    got = body.get("value") if isinstance(body, dict) else None
    if status != 0 or got != want:
        problems.append(f"{request} is well formed: expected {want!r}, got {got!r} (status {status})")

finish(problems, f"malformed requests ok: {len(INVALID)} refused, {len(ACCEPTED)} edge forms accepted")
