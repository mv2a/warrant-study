"""H9: malformed requests are refused (status 2, no output); near misses are validated, not refused (C4)."""

import json

from _cmd import call, finish

OK_RULE = {"name": "v", "type": "integer"}


def req(schema=None, rows=None, **extra):
    body = {"schema": [OK_RULE] if schema is None else schema, "rows": [] if rows is None else rows}
    body.update(extra)
    return json.dumps(body)


def rule(**fields):
    return req([{"name": "v", "type": "integer", **fields}])


REFUSED = [
    ("text that isn't JSON", "schema: v, rows: none"),
    ("empty input", ""),
    ("a JSON list", "[]"),
    ("a JSON string", '"schema"'),
    ("JSON null", "null"),
    ("truncated JSON", req()[:-3]),
    ("no schema", json.dumps({"rows": []})),
    ("no rows", json.dumps({"schema": [OK_RULE]})),
    ("an extra top-level key", req(strict=True)),
    ("an extra top-level key that is null", req(options=None)),
    ("a schema that is an object", json.dumps({"schema": {"v": "integer"}, "rows": []})),
    ("an empty schema", req([])),
    ("a schema of null", json.dumps({"schema": None, "rows": []})),
    ("a field rule that is a string", req(["v"])),
    ("a field rule with no name", req([{"type": "integer"}])),
    ("an empty name", req([{"name": "", "type": "integer"}])),
    ("a numeric name", req([{"name": 5, "type": "integer"}])),
    ("a null name", req([{"name": None, "type": "integer"}])),
    ("a repeated name", req([{"name": "v", "type": "integer"}, {"name": "v", "type": "string"}])),
    ("a field rule with no type", req([{"name": "v"}])),
    ("the type \"date\"", req([{"name": "v", "type": "date"}])),
    ("the type \"Integer\"", req([{"name": "v", "type": "Integer"}])),
    ("the type \"int\"", req([{"name": "v", "type": "int"}])),
    ("a type given as a list", req([{"name": "v", "type": ["string"]}])),
    ("an unknown key \"maximum\"", rule(maximum=3)),
    ("an unknown key \"default\"", rule(default=0)),
    ("an unknown key \"Required\"", rule(Required=True)),
    ("required \"yes\"", rule(required="yes")),
    ("required 1", rule(required=1)),
    ("required null", rule(required=None)),
    ("unique 0", rule(unique=0)),
    ("unique \"false\"", rule(unique="false")),
    ("min on a string field", req([{"name": "v", "type": "string", "min": 1}])),
    ("max on a boolean field", req([{"name": "v", "type": "boolean", "max": 1}])),
    ("min written as text", rule(min="3")),
    ("max of true", rule(max=True)),
    ("min of null", rule(min=None)),
    ("max given as a list", rule(max=[5])),
    ("min greater than max", rule(min=5, max=4)),
    ("min greater than max, as decimals", req([{"name": "v", "type": "number", "min": 0.5, "max": 0.25}])),
    ("an empty allowed list", rule(allowed=[])),
    ("allowed given as a string", req([{"name": "v", "type": "string", "allowed": "red"}])),
    ("allowed of null", rule(allowed=None)),
    ("allowed text on an integer field", rule(allowed=["1", 2])),
    ("allowed 1.5 on an integer field", rule(allowed=[1.5])),
    ("allowed true on a number field", req([{"name": "v", "type": "number", "allowed": [1, True]}])),
    ("allowed 1 on a string field", req([{"name": "v", "type": "string", "allowed": ["a", 1]}])),
    ("allowed 0 on a boolean field", req([{"name": "v", "type": "boolean", "allowed": [0]}])),
    ("allowed null on a string field", req([{"name": "v", "type": "string", "allowed": [None]}])),
    ("rows that are an object", req(rows={"0": {"v": 1}})),
    ("rows of null", json.dumps({"schema": [OK_RULE], "rows": None})),
    ("a row that is a list", req(rows=[{"v": 1}, [1]])),
    ("a row that is a string", req(rows=[{"v": 1}, "v=2"])),
    ("a row that is null", req(rows=[None])),
    ("a bad rule after a good one", req([OK_RULE, {"name": "w", "type": "text"}])),
    # JSON has no NaN or Infinity, although Python's json module reads them unless told not to.
    ("NaN as a min, which JSON does not have",
     '{"schema": [{"name": "v", "type": "number", "min": NaN}], "rows": [{"v": 1}]}'),
    ("Infinity in an allowed list, which JSON does not have",
     '{"schema": [{"name": "v", "type": "number", "allowed": [1, Infinity]}], "rows": [{"v": 1}]}'),
    ("-Infinity as a row value, which JSON does not have",
     '{"schema": [{"name": "v", "type": "number"}], "rows": [{"v": 2}, {"v": -Infinity}]}'),
]

ACCEPTED = [
    ("min equal to max", rule(min=3, max=3)),
    ("a repeated allowed value", rule(allowed=[1, 1, 2])),
    ("required and unique written as false", rule(required=False, unique=False)),
    ("a decimal min on an integer field", rule(min=0.5, allowed=[2.0])),
    ("a unique boolean field", req([{"name": "v", "type": "boolean", "unique": True}])),
    ("mixed allowed numbers on a number field", req([{"name": "v", "type": "number", "allowed": [1, 2.5], "min": -1}])),
    ("all seven keys", rule(required=True, unique=True, min=0, max=9, allowed=[1, 2])),
    ("rule keys in an unusual order", req([{"allowed": ["x"], "type": "string", "name": "v"}])),
    ("a name with spaces and symbols", req([{"name": " V-1 / total ", "type": "number"}])),
    ("rows with bad values", req(rows=[{"v": "one"}, {"v": None}, {"v": [1]}, {}])),
    ("rows with extra fields", req(rows=[{"v": 1, "w": {"deep": [None]}}])),
]

problems = []
for label, raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"{label}: expected a refusal (status 2, no output), got status {status} and {str(body)[:60]!r}")
for label, raw in ACCEPTED:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict) or "errors" not in body:
        problems.append(f"{label}: must be validated with status 0, got status {status} and {str(body)[:60]!r}")

finish(problems, f"refusals ok: {len(REFUSED)} refused, {len(ACCEPTED)} near misses validated")
