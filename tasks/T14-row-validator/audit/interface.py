"""X1 (C1): the command's interface: input and output shapes, exit statuses, row positions, field names, defaults."""

import json
import random

from _audit import e, expect, refused, request_text, run, shape_problem
from _cmd import finish
from _oracle import gen_rows, gen_schema

problems = []

# 1. Output shape on many generated requests (seeded), exit status 0 even when valid is false.
rng = random.Random(3_990_517)
shapes = 0
for _ in range(25):
    schema = gen_schema(rng)
    rows = gen_rows(rng, schema)
    status, out, err = run(request_text(schema, rows))
    shapes += 1
    if status != 0:
        problems.append(f"generated request: exited with status {status}, expected 0 ({err.strip()[:60]!r})")
        continue
    try:
        body = json.loads(out)
    except json.JSONDecodeError:
        problems.append(f"generated request: standard output is not exactly one JSON value: {out.strip()[:60]!r}")
        continue
    problem = shape_problem(body, len(rows))
    if problem:
        problems.append(f"generated request: {problem}")
        continue
    names = {rule["name"] for rule in schema}
    for error in body["errors"]:
        if error["field"] not in names:
            problems.append(f"generated request: error names a field the schema does not have: {error}")
            break

# 2. row is the zero-based position, field is the name exactly as the schema spells it.
schema = [
    {"name": "n\u00famero de s\u00f3cio", "type": "integer", "required": True},
    {"name": "Tier", "type": "string", "allowed": ["gold", "tin"]},
    {"name": "tier", "type": "string"},
]
rows = [{"n\u00famero de s\u00f3cio": 5, "Tier": "gold"}, {"n\u00famero de s\u00f3cio": 6}, {"Tier": "lead", "tier": 3}]
expect(problems, "row positions and field names", request_text(schema, rows),
       [e(2, "n\u00famero de s\u00f3cio", "missing"), e(2, "Tier", "allowed"), e(2, "tier", "type")], nrows=3)

# 3. A table with no problems: valid true, errors empty, status 0.
expect(problems, "clean table", request_text(schema, rows[:2]), [], nrows=2)

# 4. No rows at all is a valid request with a valid table.
expect(problems, "empty rows", request_text(schema, []), [], nrows=0)

# 5. required and unique are false when left out.
schema = [{"name": "tag", "type": "string"}, {"name": "w", "type": "number"}]
rows = [{"tag": "q", "w": 1}, {"tag": "q", "w": 1}, {}, {"tag": None, "w": None}]
expect(problems, "required and unique default to false", request_text(schema, rows), [], nrows=4)

# 6. All seven rule keys at once, keys in any order, and JSON spread over several lines with spaces.
schema = [{"allowed": [3, 5, 8], "max": 8, "unique": True, "min": 3, "required": True, "type": "integer", "name": "step"}]
rows = [{"step": 3}, {"step": 5}, {"step": 4}, {"step": 3.0}, {"step": 9}, {}]
text = "\n  " + json.dumps({"rows": rows, "schema": schema}, indent=3) + "\n\n"
expect(problems, "all seven keys, pretty-printed input", text,
       [e(2, "step", "allowed"), e(3, "step", "duplicate"), e(4, "step", "range"), e(5, "step", "missing")], nrows=6)

# 7. Refusals: status 2, nothing on standard output, a reason on standard error.
refusals = {
    "text that is not JSON": "rows: none",
    "an unknown field type": request_text([{"name": "at", "type": "datetime"}], [{"at": "x"}]),
    "an extra top-level key": request_text([{"name": "at", "type": "string"}], [], strict=True),
    "rows that is not a list": json.dumps({"schema": [{"name": "at", "type": "string"}], "rows": {"at": "x"}}),
}
for label, text in refusals.items():
    refused(problems, label, text)

finish(problems, f"interface ok: {shapes} generated requests, 5 fixed requests, {len(refusals)} refusals")
