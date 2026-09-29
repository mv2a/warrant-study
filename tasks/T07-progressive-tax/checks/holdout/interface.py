"""H7 (C4): one JSON object in; exactly six integer fields out with status 0; refusals print nothing."""

import json
import random

from _cmd import call, finish
from _model import FIELDS

rng = random.Random(70707)
problems = []

requests = [{"income_cents": rng.randint(0, 50_000_000), "dependents": rng.randint(0, 20)} for _ in range(30)]
requests += [{"income_cents": 0, "dependents": 0}, {"income_cents": 10**12, "dependents": 20}]
for request in requests:
    status, body = call(request)
    if status != 0:
        problems.append(f"{request}: exited with status {status}, expected 0")
    elif not isinstance(body, dict):
        problems.append(f"{request}: expected one JSON object on standard output, got {body!r}")
    elif set(body) != set(FIELDS):
        problems.append(f"{request}: expected exactly the fields {list(FIELDS)}, got {sorted(body)}")
    elif not all(type(body[field]) is int for field in FIELDS):
        problems.append(f"{request}: every field must be a JSON integer, got {body!r}")

# Other fields in the request are ignored: the response is the same as without them.
EXTRAS = [{"name": "A. Filer"}, {"year": 2026}, {"income": 5}, {"credit_cents": 99999}, {"notes": {"a": [1, 2]}}]
for extra in EXTRAS:
    plain = {"income_cents": rng.randint(0, 20_000_000), "dependents": rng.randint(0, 20)}
    _, expected = call(plain)
    status, body = call({**extra, **plain})
    if status != 0 or body != expected:
        problems.append(f"extra field {extra}: expected the same response as without it, {expected!r}, got status {status} and {body!r}")

# Pretty-printed JSON with the fields in the other order is the same request.
pretty = json.dumps({"dependents": 2, "income_cents": 9500000}, indent=4)
status, body = call(raw=pretty)
_, compact = call({"income_cents": 9500000, "dependents": 2})
if status != 0 or body != compact:
    problems.append(f"a pretty-printed request should get the same response, got status {status} and {body!r}")

# A refused request exits with status 2 and writes nothing on standard output.
REFUSED = ["not json", "[1, 2]", '{"income_cents": -5, "dependents": 0}', '{"income_cents": 100, "dependents": 21}',
           '{"income_cents": 100}', '{"income_cents": 100.5, "dependents": 0}']
for raw in REFUSED:
    status, body = call(raw=raw)
    if status != 2 or body is not None:
        problems.append(f"refused request {raw!r}: expected status 2 and nothing on standard output, got status {status} and {body!r}")

finish(problems, f"interface ok: {len(requests)} responses, {len(EXTRAS)} extra fields, {len(REFUSED)} refusals")
