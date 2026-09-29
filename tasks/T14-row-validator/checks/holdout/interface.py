"""H6: the input and output shapes, zero-based rows, `valid`, and how a refusal looks (C1)."""

import json
import subprocess

from _cmd import PATH, call, finish

CODES = {"missing", "type", "range", "allowed", "duplicate"}
problems = []


def shape_problems(label, body):
    if not isinstance(body, dict) or set(body) != {"valid", "errors"}:
        return [f"{label}: expected an object with exactly valid and errors, got {body!r}"]
    out = []
    if type(body["valid"]) is not bool or not isinstance(body["errors"], list):
        return [f"{label}: valid must be true or false and errors a list, got {body!r}"]
    if body["valid"] != (body["errors"] == []):
        out.append(f"{label}: valid must be true exactly when errors is empty, got {body!r}")
    for err in body["errors"]:
        if not isinstance(err, dict) or set(err) != {"row", "field", "code"}:
            out.append(f"{label}: each error needs exactly row, field and code, got {err!r}")
        elif type(err["row"]) is not int or type(err["field"]) is not str or err["code"] not in CODES:
            out.append(f"{label}: badly typed error {err!r}")
    return out


SCHEMA = [{"name": "k", "type": "integer", "required": True}, {"name": "label", "type": "string"}]

# Zero-based row positions.
for n in (1, 2, 10, 57):
    rows = [{"k": i} for i in range(n)]
    rows[-1] = {"label": "no k"}
    status, body = call({"schema": SCHEMA, "rows": rows})
    want = {"valid": False, "errors": [{"row": n - 1, "field": "k", "code": "missing"}]}
    problems += shape_problems(f"{n} rows", body)
    if status != 0 or body != want:
        problems.append(f"{n} rows, last one bad: expected status 0 and {want}, got status {status} and {body!r}")

# Valid data, including no rows at all.
for rows in ([], [{"k": 1}], [{"k": 1, "label": "x"}, {"k": 2}]):
    status, body = call({"schema": SCHEMA, "rows": rows})
    problems += shape_problems(f"rows {rows}", body)
    if status != 0 or body != {"valid": True, "errors": []}:
        problems.append(f"rows {rows}: expected status 0 and valid true with no errors, got status {status} and {body!r}")

# Key order and whitespace in the request do not matter.
raw = '\n  {\n "rows" : [ {"label": 5} ] ,\n\t"schema": [ {"type": "string", "name": "label"} ]\n}\n'
status, body = call(raw=raw)
if status != 0 or body != {"valid": False, "errors": [{"row": 0, "field": "label", "code": "type"}]}:
    problems.append(f"a pretty-printed request with rows before schema: got status {status} and {body!r}")

# Standard output holds exactly one JSON object; a refusal leaves it empty and explains on stderr.
done = subprocess.run([PATH], input=json.dumps({"schema": SCHEMA, "rows": [{"k": "1"}]}), capture_output=True, text=True, timeout=10)
try:
    parsed = json.loads(done.stdout)
except json.JSONDecodeError:
    parsed = None
if done.returncode != 0 or not isinstance(parsed, dict):
    problems.append(f"standard output must be exactly one JSON object, got status {done.returncode} and {done.stdout[:80]!r}")
for label, text in (("text that isn't JSON", "rows please"), ("a schema of type \"text\"", json.dumps({"schema": [{"name": "k", "type": "text"}], "rows": []}))):
    done = subprocess.run([PATH], input=text, capture_output=True, text=True, timeout=10)
    if done.returncode != 2 or done.stdout.strip() or not done.stderr.strip():
        problems.append(f"{label}: a refusal needs status 2, empty standard output and a reason on standard error; got status {done.returncode}, stdout {done.stdout[:60]!r}, stderr {done.stderr[:60]!r}")

finish(problems, "interface ok: 4 row counts, 3 valid tables, reordered request, stdout and refusals")
