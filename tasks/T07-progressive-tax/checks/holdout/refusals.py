"""H6 (C3): invalid requests are refused with exit status 2, and valid edge cases are not refused."""

from _cmd import call, finish

INVALID = [
    ("text that isn't JSON", "thirty thousand marks"),
    ("an empty request", ""),
    ("a cut-off JSON object", '{"income_cents": 3000000, "dependents": 0'),
    ("a list instead of an object", "[3000000, 0]"),
    ("a bare number", "3000000"),
    ("null", "null"),
    ("an empty object", "{}"),
    ("a missing income", '{"dependents": 1}'),
    ("a missing dependents count", '{"income_cents": 3000000}'),
    ("a negative income", '{"income_cents": -1, "dependents": 0}'),
    ("a large negative income", '{"income_cents": -3000000, "dependents": 2}'),
    ("a fractional income", '{"income_cents": 3000000.5, "dependents": 0}'),
    ("an income written 3000000.0", '{"income_cents": 3000000.0, "dependents": 0}'),
    ("an income in exponent form", '{"income_cents": 3e6, "dependents": 0}'),
    ("an income written as text", '{"income_cents": "3000000", "dependents": 0}'),
    ("an income of true", '{"income_cents": true, "dependents": 0}'),
    ("an income of false", '{"income_cents": false, "dependents": 0}'),
    ("an income of null", '{"income_cents": null, "dependents": 0}'),
    ("an income in a list", '{"income_cents": [3000000], "dependents": 0}'),
    ("a negative dependents count", '{"income_cents": 3000000, "dependents": -1}'),
    ("21 dependents", '{"income_cents": 3000000, "dependents": 21}'),
    ("100 dependents", '{"income_cents": 3000000, "dependents": 100}'),
    ("a fractional dependents count", '{"income_cents": 3000000, "dependents": 2.5}'),
    ("a dependents count written 2.0", '{"income_cents": 3000000, "dependents": 2.0}'),
    ("a dependents count written as text", '{"income_cents": 3000000, "dependents": "2"}'),
    ("a dependents count of true", '{"income_cents": 3000000, "dependents": true}'),
    ("a dependents count of false", '{"income_cents": 3000000, "dependents": false}'),
    ("a dependents count of null", '{"income_cents": 3000000, "dependents": null}'),
    ("a second object after the request", '{"income_cents": 3000000, "dependents": 0}\n{"income_cents": 5, "dependents": 1}'),
    ("text after the request", '{"income_cents": 3000000, "dependents": 0} end'),
]
VALID = [
    ("no income and no dependents", '{"income_cents": 0, "dependents": 0}'),
    ("one cent of income", '{"income_cents": 1, "dependents": 0}'),
    ("20 dependents", '{"income_cents": 3000000, "dependents": 20}'),
    ("a very large income", '{"income_cents": 10000000000000, "dependents": 3}'),
    ("an extra field", '{"income_cents": 3000000, "dependents": 1, "name": "A. Filer"}'),
    ("whitespace around the request", ' \n{"income_cents": 3000000, "dependents": 1}\n\t \n'),
]
problems = []
for name, raw in INVALID:
    status, body = call(raw=raw)
    taxed = isinstance(body, dict) and "tax_cents" in body
    if status != 2 or taxed:
        problems.append(f"{name}: expected a refusal with status 2, got status {status} and {body!r}")
for name, raw in VALID:
    status, body = call(raw=raw)
    if status != 0 or not isinstance(body, dict) or "tax_cents" not in body:
        problems.append(f"{name}: expected to be taxed with status 0, got status {status} and {body!r}")

finish(problems, f"refusals ok: {len(INVALID)} invalid and {len(VALID)} valid requests")
