"""P1: `validate` follows the interface in C1, and refuses one malformed schema (C4)."""

from _cmd import call, finish

CODES = {"missing", "type", "range", "allowed", "duplicate"}
SCHEMA = [
    {"name": "sku", "type": "string", "required": True, "unique": True},
    {"name": "qty", "type": "integer", "min": 0},
]
REQUESTS = [
    {"schema": SCHEMA, "rows": [{"sku": "A-1", "qty": 3}, {"sku": "B-2"}]},
    {"schema": SCHEMA, "rows": [{"sku": "A-1", "qty": 3}, {"qty": -1}]},
]
problems = []

for request in REQUESTS:
    status, body = call(request)
    if status != 0:
        problems.append(f"rows {request['rows']}: exited with status {status}, expected 0")
        continue
    if not isinstance(body, dict) or set(body) != {"valid", "errors"}:
        problems.append(f"rows {request['rows']}: expected an object with exactly valid and errors, got {body!r}")
        continue
    errors = body["errors"]
    if type(body["valid"]) is not bool or not isinstance(errors, list):
        problems.append(f"rows {request['rows']}: valid must be true or false and errors a list, got {body!r}")
        continue
    if body["valid"] != (errors == []):
        problems.append(f"rows {request['rows']}: valid must be true exactly when errors is empty, got {body!r}")
    for error in errors:
        if not isinstance(error, dict) or set(error) != {"row", "field", "code"}:
            problems.append(f"each error needs exactly row, field and code, got {error!r}")
        elif type(error["row"]) is not int or not isinstance(error["field"], str) or error["code"] not in CODES:
            problems.append(f"an error has a badly typed row, field or code: {error!r}")

status, body = call({"schema": [{"name": "when", "type": "date"}], "rows": []})
if status != 2 or body is not None:
    problems.append(f"a field of type \"date\" must be refused with status 2 and no output, got status {status} and {body!r}")

finish(problems, "contract ok: 3 requests")
